"""YouBike 查詢邏輯（僅在 USE_TDX=true 時提供，沒有模擬資料備援）。"""
from app.core.config import tdx_enabled
from app.schemas.bike import BikeStation
from app.services import tdx_bike_service
from app.services.geo import haversine_meters


async def get_nearby_bike_stations(lat: float, lng: float) -> list[BikeStation] | None:
    """回傳附近 YouBike 站點（依距離排序）；USE_TDX=false 時回傳 None 表示此功能未啟用。"""
    if not tdx_enabled():
        return None

    stations = await tdx_bike_service.fetch_nearby_bike_stations_tdx(lat, lng)
    for station in stations:
        station["distance_meters"] = round(
            haversine_meters(lat, lng, station["lat"], station["lng"])
        )
    stations.sort(key=lambda item: item["distance_meters"])

    return [
        BikeStation(
            id=station["id"],
            name=station["name"],
            address=station["address"],
            lat=station["lat"],
            lng=station["lng"],
            capacity=station["capacity"],
            available_rent=station["available_rent"],
            available_rent_general=station["available_rent_general"],
            available_rent_electric=station["available_rent_electric"],
            available_return=station["available_return"],
            status=station["status"],
            distance_meters=station["distance_meters"],
        )
        for station in stations[:30]
    ]
