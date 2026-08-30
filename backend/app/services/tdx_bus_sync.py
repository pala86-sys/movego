"""把 TDX 公車路線／站牌資料批次同步進 SQLite（一次性，之後查詢改讀本機）。"""
import logging

from sqlalchemy.orm import Session

from app.db.models import BusRouteModel, BusRouteStopModel
from app.services import tdx_bus_service
from app.services.tdx_bus_service import DIRECTION_KEYS, DIRECTION_LABELS, make_route_id
from app.services.tdx_common import zh_text as _zh

logger = logging.getLogger(__name__)

# 少於這個數字視為還是模擬資料／尚未同步過，值得花額度重新同步一次；
# 一旦同步成功會有上千條路線，遠高於這個門檻，重啟時就不會又浪費額度重打。
REAL_DATA_THRESHOLD = 50


async def sync_bus_routes_to_db(db: Session) -> int:
    """回傳成功寫入的路線數量。呼叫端需自行 try/except：失敗時維持既有資料（通常是模擬資料）。"""
    routes = await tdx_bus_service.fetch_all_routes_tdx()
    stop_entries = await tdx_bus_service.fetch_all_stop_of_route_tdx()

    grouped: dict[tuple[str, str], dict[int, list[dict]]] = {}
    for entry in stop_entries:
        key = (entry["city"], entry["name"])
        grouped.setdefault(key, {})[entry["direction"]] = entry["stops"]

    route_meta = {(r["city"], r["name"]): r for r in routes}

    db.query(BusRouteStopModel).delete()
    db.query(BusRouteModel).delete()

    count = 0
    for (city, name), directions in grouped.items():
        if 0 not in directions or 1 not in directions:
            continue  # 只收錄去回程站牌都齊全的路線
        meta = route_meta.get((city, name), {"operator": ""})
        route_model = BusRouteModel(id=make_route_id(city, name), name=name, operator=meta.get("operator", ""), city=city)
        for direction, stops in directions.items():
            direction_key = DIRECTION_KEYS[direction]
            direction_label = DIRECTION_LABELS[direction]
            from_name = _zh(stops[0].get("StopName"))
            to_name = _zh(stops[-1].get("StopName"))
            for seq, stop in enumerate(stops):
                route_model.stops.append(
                    BusRouteStopModel(
                        direction=direction_key,
                        direction_label=direction_label,
                        from_name=from_name,
                        to_name=to_name,
                        seq=seq,
                        stop_name=_zh(stop.get("StopName")),
                        stop_uid=stop.get("StopUID", ""),
                    )
                )
        db.add(route_model)
        count += 1

    db.commit()
    return count


async def sync_bus_routes_if_needed(db: Session) -> None:
    existing_count = db.query(BusRouteModel).count()
    if existing_count >= REAL_DATA_THRESHOLD:
        logger.info("公車資料庫已有 %d 條路線，略過重新同步", existing_count)
        return
    try:
        count = await sync_bus_routes_to_db(db)
        logger.info("TDX 公車資料同步完成，共 %d 條路線", count)
    except Exception as exc:  # noqa: BLE001 - 同步失敗不該讓整個 app 起不來，維持既有（模擬）資料即可
        logger.warning("TDX 公車資料同步失敗，維持現有資料：%s", exc)
