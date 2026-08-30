"""TDX 停車場資料轉換：附近路外停車場基本資料 + 即時剩餘車位。

跟公車/捷運不同，停車資訊是掛在 TDX 的 /v1/Parking（不是 /v2）底下，
而且回傳格式是「包一層外殼物件」而不是直接一個陣列（例如 CarPark 回傳
{..., "CarParks": [...]}），這裡統一處理掉這個差異。

座標查詢跟使用者當下位置有關，沒辦法預先批次同步，維持即時呼叫 TDX。
"""
from app.services.tdx_client import tdx_get
from app.services.tdx_common import CITIES, zh_text as _zh


def _status_from_availability(entry: dict | None) -> tuple[str, int | None, int | None]:
    if entry is None:
        return "無即時資料", None, None
    total = entry.get("TotalSpaces")
    available = entry.get("AvailableSpaces")
    if entry.get("FullStatus") == 1:
        return "已滿", total, available
    if entry.get("ServiceStatus") not in (1, None):
        return "非服務時間", total, available
    return "正常", total, available


async def fetch_nearby_parking_lots_tdx(lat: float, lng: float, radius_m: int = 800) -> list[dict]:
    """回傳指定座標附近的路外停車場，含即時剩餘車位（合併台北市與新北市）。"""
    lots_by_id: dict[str, dict] = {}
    for city in CITIES:
        data = await tdx_get(
            f"/v1/Parking/OffStreet/CarPark/City/{city}",
            {"$spatialFilter": f"nearby({lat},{lng},{radius_m})"},
        )
        for item in data.get("CarParks", []) if isinstance(data, dict) else []:
            car_park_id = item.get("CarParkID")
            name = _zh(item.get("CarParkName"))
            if not car_park_id or not name:
                continue
            position = item.get("CarParkPosition") or {}
            lots_by_id[car_park_id] = {
                "id": car_park_id,
                "name": name,
                "address": item.get("Address", ""),
                "lat": position.get("PositionLat", lat),
                "lng": position.get("PositionLon", lng),
                "city": city,
            }

    if not lots_by_id:
        return []

    availability_by_id: dict[str, dict] = {}
    for city in CITIES:
        data = await tdx_get(f"/v1/Parking/OffStreet/ParkingAvailability/City/{city}")
        for item in data.get("ParkingAvailabilities", []) if isinstance(data, dict) else []:
            car_park_id = item.get("CarParkID")
            if car_park_id:
                availability_by_id[car_park_id] = item

    results = []
    for car_park_id, lot in lots_by_id.items():
        status, total, available = _status_from_availability(availability_by_id.get(car_park_id))
        results.append(
            {
                "id": lot["id"],
                "name": lot["name"],
                "address": lot["address"],
                "lat": lot["lat"],
                "lng": lot["lng"],
                "total_spaces": total,
                "available_spaces": available,
                "status": status,
            }
        )
    return results
