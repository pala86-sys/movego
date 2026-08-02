"""停車場查詢邏輯（僅在 USE_TDX=true 時提供，沒有模擬資料備援）。"""
from app.core.config import get_settings
from app.schemas.parking import ParkingLot
from app.services import tdx_parking_service
from app.services.geo import haversine_meters


async def get_nearby_parking_lots(lat: float, lng: float) -> list[ParkingLot] | None:
    """回傳附近停車場（依距離排序）；USE_TDX=false 時回傳 None 表示此功能未啟用。"""
    if not get_settings().use_tdx:
        return None

    lots = await tdx_parking_service.fetch_nearby_parking_lots_tdx(lat, lng)
    for lot in lots:
        lot["distance_meters"] = round(haversine_meters(lat, lng, lot["lat"], lot["lng"]))
    lots.sort(key=lambda item: item["distance_meters"])

    return [
        ParkingLot(
            id=lot["id"],
            name=lot["name"],
            address=lot["address"],
            lat=lot["lat"],
            lng=lot["lng"],
            total_spaces=lot["total_spaces"],
            available_spaces=lot["available_spaces"],
            status=lot["status"],
            distance_meters=lot["distance_meters"],
        )
        for lot in lots[:30]
    ]
