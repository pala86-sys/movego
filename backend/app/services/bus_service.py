"""公車資料存取邏輯。

USE_TDX=false（預設）時使用 SQLite 內的模擬資料；USE_TDX=true 時改為即時呼叫 TDX，
失敗時直接向上拋出例外，由 router 轉成「目前無法取得即時資料」，不會偷偷退回模擬資料。
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
    """從 SQLite 讀取公車路線與去回程站牌（結果快取，因參考資料為靜態資料）。"""
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
                    "stops": [s.stop_name for s in stops],
                }
            routes.append(
                {
                    "id": route.id,
                    "name": route.name,
                    "operator": route.operator,
                    "outbound": directions["outbound"],
                    "inbound": directions["inbound"],
                }
            )
        return routes


async def search_routes(keyword: str) -> list[BusRouteSummary]:
    if get_settings().use_tdx:
        return await tdx_bus_service.search_routes_tdx(keyword)
    return _search_routes_mock(keyword)


def _search_routes_mock(keyword: str) -> list[BusRouteSummary]:
    keyword = keyword.strip()
    result = []
    for route in _load_raw_routes():
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


def _build_direction(raw_direction: dict, route_id: str) -> BusDirection:
    stops = [
        BusStopArrival(
            stop_name=name,
            status=mock_arrival_status(route_id, raw_direction["direction"], name),
        )
        for name in raw_direction["stops"]
    ]
    return BusDirection(
        direction=raw_direction["direction"],
        **{"from_": raw_direction["from"], "to": raw_direction["to"]},
        stops=stops,
    )


async def get_route_detail(route_id: str) -> BusRoute | None:
    if get_settings().use_tdx:
        return await tdx_bus_service.get_route_detail_tdx(route_id)
    return _get_route_detail_mock(route_id)


def _get_route_detail_mock(route_id: str) -> BusRoute | None:
    for route in _load_raw_routes():
        if route["id"].lower() == route_id.lower():
            return BusRoute(
                id=route["id"],
                name=route["name"],
                operator=route["operator"],
                outbound=_build_direction(route["outbound"], route["id"]),
                inbound=_build_direction(route["inbound"], route["id"]),
            )
    return None
