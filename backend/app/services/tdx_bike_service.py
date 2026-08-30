"""TDX 公共自行車（YouBike）資料轉換：附近站點基本資料 + 即時可借/可還。

跟停車場一樣，站點座標查詢跟使用者當下位置有關，沒辦法預先批次同步，維持即時呼叫 TDX。
站點基本資料走 /v2/Bike/Station，即時車況走 /v2/Bike/Availability，兩者用 StationUID 對起來。
"""
from app.services.tdx_client import tdx_get
from app.services.tdx_common import CITIES, zh_text as _zh

# TDX Bike Availability 的 ServiceStatus：0=停止營運, 1=正常, 2=暫停營運
_STATUS_LABELS = {0: "停止營運", 1: "正常", 2: "暫停營運"}


def _status_from_availability(entry: dict | None) -> tuple[str, int | None, int | None, int | None, int | None]:
    """回傳 (狀態字串, 可借總數, 一般車, 電輔車, 可還空位)。"""
    if entry is None:
        return "無即時資料", None, None, None, None
    rent = entry.get("AvailableRentBikes")
    ret = entry.get("AvailableReturnBikes")
    detail = entry.get("AvailableRentBikesDetail") or {}
    general = detail.get("GeneralBikes")
    electric = detail.get("ElectricBikes")
    label = _STATUS_LABELS.get(entry.get("ServiceStatus"), "正常")
    return label, rent, general, electric, ret


async def fetch_nearby_bike_stations_tdx(lat: float, lng: float, radius_m: int = 500) -> list[dict]:
    """回傳指定座標附近的 YouBike 站點，含即時可借/可還（合併台北市與新北市）。"""
    stations_by_uid: dict[str, dict] = {}
    for city in CITIES:
        data = await tdx_get(
            f"/v2/Bike/Station/City/{city}",
            {"$spatialFilter": f"nearby({lat},{lng},{radius_m})", "$top": 30},
        )
        for item in data if isinstance(data, list) else []:
            station_uid = item.get("StationUID")
            name = _zh(item.get("StationName"))
            if not station_uid or not name:
                continue
            position = item.get("StationPosition") or {}
            stations_by_uid[station_uid] = {
                "id": station_uid,
                "name": name,
                "address": _zh(item.get("StationAddress")),
                "lat": position.get("PositionLat", lat),
                "lng": position.get("PositionLon", lng),
                "capacity": item.get("BikesCapacity"),
            }

    if not stations_by_uid:
        return []

    availability_by_uid: dict[str, dict] = {}
    for city in CITIES:
        data = await tdx_get(f"/v2/Bike/Availability/City/{city}")
        for item in data if isinstance(data, list) else []:
            station_uid = item.get("StationUID")
            if station_uid:
                availability_by_uid[station_uid] = item

    results = []
    for station_uid, station in stations_by_uid.items():
        status, rent, general, electric, ret = _status_from_availability(availability_by_uid.get(station_uid))
        results.append(
            {
                **station,
                "status": status,
                "available_rent": rent,
                "available_rent_general": general,
                "available_rent_electric": electric,
                "available_return": ret,
            }
        )
    return results
