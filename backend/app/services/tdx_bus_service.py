"""TDX 公車資料轉換。

路線／站牌是很少變動的靜態參考資料，所以採「一次性批次同步」策略：
啟動時把台北市＋新北市全部路線與站牌一次抓進 SQLite（見 tdx_bus_sync.py），
之後搜尋、瀏覽路線一律讀本機資料庫，不會再即時打 TDX。
只有「到站狀態」是真正需要即時性的資料，才會在查看路線詳情時呼叫 TDX，
且有短時間快取吸收重複瀏覽，盡量不浪費免費額度。

欄位名稱依 TDX Basic API v2 Bus 資料集；若 TDX 回傳格式有異動，個別欄位讀取皆使用 .get()
防呆，寧可缺欄位也不要讓整支 API 掛掉。
"""
from app.services.tdx_client import tdx_get
from app.services.tdx_common import CITIES, zh_text as _zh
from app.services.ttl_cache import async_ttl_cache

DIRECTION_LABELS = {0: "去程", 1: "返程"}
DIRECTION_KEYS = {0: "outbound", 1: "inbound"}


def make_route_id(city: str, route_name: str) -> str:
    return f"{city}:{route_name}"


def parse_route_id(route_id: str) -> tuple[str, str]:
    if ":" in route_id:
        city, name = route_id.split(":", 1)
        if city in CITIES:
            return city, name
    # 未帶城市前綴時，預設先嘗試台北市（向下相容手動輸入的路線號碼）
    return CITIES[0], route_id


async def fetch_all_routes_tdx() -> list[dict]:
    """一次抓台北市＋新北市全部路線的基本資料（不含站牌），共 2 次 TDX 呼叫。"""
    routes: list[dict] = []
    for city in CITIES:
        data = await tdx_get(f"/v2/Bus/Route/City/{city}", {"$top": 2000})
        for item in data if isinstance(data, list) else []:
            name = _zh(item.get("RouteName"))
            if not name:
                continue
            operator = ""
            if item.get("Operators"):
                operator = item["Operators"][0].get("OperatorName", {}).get("Zh_tw", "")
            routes.append({"city": city, "name": name, "operator": operator})
    return routes


async def fetch_all_stop_of_route_tdx() -> list[dict]:
    """一次抓台北市＋新北市『全部路線』的去回程站牌，共 2 次 TDX 呼叫（不用逐條路線各打一次）。"""
    entries: list[dict] = []
    for city in CITIES:
        data = await tdx_get(f"/v2/Bus/StopOfRoute/City/{city}", {"$top": 3000})
        for entry in data if isinstance(data, list) else []:
            direction = entry.get("Direction")
            name = _zh(entry.get("RouteName"))
            if not name or direction not in (0, 1):
                continue
            stops = sorted(entry.get("Stops", []), key=lambda s: s.get("StopSequence", 0))
            if not stops:
                continue
            entries.append({"city": city, "name": name, "direction": direction, "stops": stops})
    return entries


@async_ttl_cache(60)  # 免費額度很緊，優先保護額度而非到站時間的絕對新鮮度
async def fetch_eta_by_stop_uid(city: str, route_name: str) -> dict[str, dict]:
    """回傳指定路線的即時到站資料，key 為 StopUID；去回程都包含在同一次呼叫的結果裡。"""
    data = await tdx_get(f"/v2/Bus/EstimatedTimeOfArrival/City/{city}/{route_name}")
    result: dict[str, dict] = {}
    for entry in data if isinstance(data, list) else []:
        stop_uid = entry.get("StopUID")
        if stop_uid:
            result[stop_uid] = entry
    return result


def status_from_eta(entry: dict | None) -> str:
    if entry is None:
        return "尚未發車"
    stop_status = entry.get("StopStatus", 0)
    if stop_status == 1:
        return "尚未發車"
    estimate = entry.get("EstimateTime")
    if estimate is None:
        return "尚未發車"
    if estimate <= 30:
        return "進站中"
    minutes = max(round(estimate / 60), 1)
    return f"約 {minutes} 分鐘"


async def fetch_nearby_stops_tdx(lat: float, lng: float, radius_m: int = 500) -> list[dict]:
    """回傳指定座標附近的真實公車站牌（合併台北市與新北市）。

    這個查詢跟使用者當下位置有關，沒辦法預先批次同步，所以還是即時呼叫 TDX。
    同一站名可能有多個站牌（不同去回程／不同月台位置），這裡依站名合併成一筆，
    只保留離查詢點最近的座標，避免列表出現大量重複站名。
    """
    by_name: dict[str, dict] = {}
    for city in CITIES:
        data = await tdx_get(
            f"/v2/Bus/Stop/City/{city}",
            {"$spatialFilter": f"nearby({lat},{lng},{radius_m})", "$top": 30},
        )
        for item in data if isinstance(data, list) else []:
            stop_uid = item.get("StopUID")
            name = _zh(item.get("StopName"))
            if not stop_uid or not name:
                continue
            position = item.get("StopPosition") or {}
            if name not in by_name:
                by_name[name] = {
                    "id": stop_uid,
                    "name": name,
                    "type": "bus",
                    "lat": position.get("PositionLat", lat),
                    "lng": position.get("PositionLon", lng),
                    "lines": [],
                    "routes": [],
                }
    return list(by_name.values())
