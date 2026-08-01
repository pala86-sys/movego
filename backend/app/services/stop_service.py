"""站牌搜尋與附近站牌邏輯。"""
from functools import lru_cache

from app.db.database import SessionLocal
from app.db.models import NearbyStopModel
from app.schemas.stop import NearbyStop, RouteAtStop, StopSearchResult
from app.services.bus_service import _load_raw_routes
from app.services.realtime_service import mock_arrival_status


@lru_cache
def _load_nearby() -> list[dict]:
    """從 SQLite 讀取模擬的附近站牌清單。"""
    with SessionLocal() as db:
        return [
            {
                "id": s.id,
                "name": s.name,
                "type": s.type,
                "lat": s.lat,
                "lng": s.lng,
                "lines": [x for x in s.lines_csv.split(",") if x],
                "routes": [x for x in s.routes_csv.split(",") if x],
            }
            for s in db.query(NearbyStopModel).all()
        ]


def search_stop(keyword: str) -> list[StopSearchResult]:
    """依站牌名稱搜尋，回傳該站牌上所有經過的公車路線與模擬到站狀態。"""
    keyword = keyword.strip()
    if not keyword:
        return []

    matched_names: set[str] = set()
    for route in _load_raw_routes():
        for direction in (route["outbound"], route["inbound"]):
            for stop_name in direction["stops"]:
                if keyword in stop_name:
                    matched_names.add(stop_name)

    results: list[StopSearchResult] = []
    for stop_name in sorted(matched_names):
        routes: list[RouteAtStop] = []
        for route in _load_raw_routes():
            for direction in (route["outbound"], route["inbound"]):
                if stop_name in direction["stops"]:
                    routes.append(
                        RouteAtStop(
                            route_id=route["id"],
                            route_name=route["name"],
                            direction=direction["direction"],
                            status=mock_arrival_status(route["id"], direction["direction"], stop_name),
                        )
                    )
        results.append(StopSearchResult(stop_name=stop_name, routes=routes))

    return results


def get_nearby_stops() -> list[NearbyStop]:
    """回傳模擬的「附近站牌」清單（第一版尚未接真實定位距離運算）。"""
    stops = []
    for item in _load_nearby():
        stops.append(
            NearbyStop(
                id=item["id"],
                name=item["name"],
                type=item["type"],
                lat=item["lat"],
                lng=item["lng"],
                lines=item.get("lines", []),
                routes=item.get("routes", []),
                distance_meters=None,
            )
        )
    return stops
