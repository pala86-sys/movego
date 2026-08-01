"""公車資料存取邏輯。

路線／站牌一律讀 SQLite（USE_TDX=false 時是內建 5 條示範路線；USE_TDX=true 時是
啟動時從 TDX 批次同步進來的全量真實路線，見 tdx_bus_sync.py），搜尋與瀏覽路線
完全不會即時打 TDX。只有查看路線詳情時，如果 USE_TDX=true，才會額外打 1 次 TDX
取得該路線的即時到站狀態（已快取，見 tdx_bus_service.fetch_eta_by_stop_uid）。
"""
from functools import lru_cache

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import BusRouteModel
from app.schemas.bus import BusDirection, BusRoute, BusRouteSummary, BusStopArrival
from app.services import tdx_bus_service
from app.services.realtime_service import mock_arrival_status


@lru_cache
def _load_raw_routes() -> list[dict]:
    """從 SQLite 讀取公車路線與去回程站牌（結果快取，因為同一次啟動內資料不會變動）。"""
    with SessionLocal() as db:
        route_models = db.query(BusRouteModel).all()
        routes: list[dict] = []
        for route in route_models:
            directions: dict[str, dict] = {"outbound": None, "inbound": None}
            for direction_key in ("outbound", "inbound"):
                stops = [s for s in route.stops if s.direction == direction_key]
                if not stops:
                    continue
                directions[direction_key] = {
                    "direction": stops[0].direction_label,
                    "from": stops[0].from_name,
                    "to": stops[0].to_name,
                    "stops": [{"name": s.stop_name, "stop_uid": s.stop_uid} for s in stops],
                }
            routes.append(
                {
                    "id": route.id,
                    "name": route.name,
                    "operator": route.operator,
                    "city": route.city,
                    "outbound": directions["outbound"],
                    "inbound": directions["inbound"],
                }
            )
        return routes


def search_routes(keyword: str) -> list[BusRouteSummary]:
    keyword = keyword.strip()
    result = []
    for route in _load_raw_routes():
        if not route["outbound"]:
            continue
        if keyword and keyword.lower() not in route["name"].lower():
            continue
        result.append(
            BusRouteSummary(
                id=route["id"],
                name=route["name"],
                operator=route["operator"],
                **{"from_": route["outbound"]["from"], "to": route["outbound"]["to"]},
            )
        )
    return result


def _build_direction(raw_direction: dict, route_id: str, eta_by_uid: dict[str, dict] | None) -> BusDirection:
    stops = []
    for stop in raw_direction["stops"]:
        if eta_by_uid is not None:
            status = tdx_bus_service.status_from_eta(eta_by_uid.get(stop["stop_uid"]))
            is_mock = False
        else:
            status = mock_arrival_status(route_id, raw_direction["direction"], stop["name"])
            is_mock = True
        stops.append(BusStopArrival(stop_name=stop["name"], status=status, is_mock=is_mock))
    return BusDirection(
        direction=raw_direction["direction"],
        **{"from_": raw_direction["from"], "to": raw_direction["to"]},
        stops=stops,
    )


async def get_route_detail(route_id: str) -> BusRoute | None:
    matched = None
    for route in _load_raw_routes():
        if route["id"].lower() == route_id.lower():
            matched = route
            break
    if matched is None or not matched["outbound"] or not matched["inbound"]:
        return None

    eta_by_uid: dict[str, dict] | None = None
    if get_settings().use_tdx:
        eta_by_uid = await tdx_bus_service.fetch_eta_by_stop_uid(matched["city"], matched["name"])

    return BusRoute(
        id=matched["id"],
        name=matched["name"],
        operator=matched["operator"],
        outbound=_build_direction(matched["outbound"], matched["id"], eta_by_uid),
        inbound=_build_direction(matched["inbound"], matched["id"], eta_by_uid),
    )
