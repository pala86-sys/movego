"""站牌搜尋與附近站牌邏輯。"""
import asyncio
import math
from functools import lru_cache

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import NearbyStopModel
from app.schemas.stop import NearbyStop, RouteAtStop, StopSearchResult
from app.services import tdx_bus_service, tdx_metro_service
from app.services.bus_service import _load_raw_routes
from app.services.realtime_service import mock_arrival_status

# 找不到定位權限時，預設以台北車站為中心搜尋附近站牌
DEFAULT_CENTER = (25.0478, 121.5170)


def _haversine_meters(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    r = 6371000
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


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


async def get_nearby_stops(lat: float | None = None, lng: float | None = None) -> list[NearbyStop]:
    """依座標回傳附近站牌；USE_TDX=true 時為真實資料並依距離排序，否則回傳固定模擬清單。"""
    if not get_settings().use_tdx:
        return _get_nearby_stops_mock()

    center_lat, center_lng = (lat, lng) if lat is not None and lng is not None else DEFAULT_CENTER

    bus_stops, metro_stations = await asyncio.gather(
        tdx_bus_service.fetch_nearby_stops_tdx(center_lat, center_lng),
        tdx_metro_service.fetch_nearby_stations_tdx(center_lat, center_lng),
    )

    combined = bus_stops + metro_stations
    for item in combined:
        item["distance_meters"] = round(_haversine_meters(center_lat, center_lng, item["lat"], item["lng"]))
    combined.sort(key=lambda item: item["distance_meters"])

    return [
        NearbyStop(
            id=item["id"],
            name=item["name"],
            type=item["type"],
            lat=item["lat"],
            lng=item["lng"],
            lines=item.get("lines", []),
            routes=item.get("routes", []),
            distance_meters=item["distance_meters"],
        )
        for item in combined[:30]
    ]


def _get_nearby_stops_mock() -> list[NearbyStop]:
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
