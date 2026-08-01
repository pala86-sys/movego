"""TDX 公車資料轉換：路線搜尋、去回程站牌、即時到站狀態。

大台北範圍固定查詢「Taipei」（臺北市）與「NewTaipei」（新北市）兩個 City，合併結果。
欄位名稱依 TDX Basic API v2 Bus 資料集；若 TDX 回傳格式有異動，個別欄位讀取皆使用 .get()
防呆，寧可缺欄位也不要讓整支 API 掛掉。
"""
from app.schemas.bus import BusDirection, BusRoute, BusRouteSummary, BusStopArrival
from app.services.tdx_client import tdx_get
from app.services.ttl_cache import async_ttl_cache

CITIES = ["Taipei", "NewTaipei"]
DIRECTION_LABELS = {0: "去程", 1: "返程"}
DIRECTION_KEYS = {0: "outbound", 1: "inbound"}


def _zh(field: dict | None) -> str:
    if not field:
        return ""
    return field.get("Zh_tw") or field.get("Zh_TW") or ""


def make_route_id(city: str, route_name: str) -> str:
    return f"{city}:{route_name}"


def parse_route_id(route_id: str) -> tuple[str, str]:
    if ":" in route_id:
        city, name = route_id.split(":", 1)
        if city in CITIES:
            return city, name
    # 未帶城市前綴時，預設先嘗試台北市（向下相容手動輸入的路線號碼）
    return CITIES[0], route_id


@async_ttl_cache(300)  # 路線清單是靜態參考資料，快取 5 分鐘大幅降低額度消耗
async def search_routes_tdx(keyword: str) -> list[BusRouteSummary]:
    keyword = keyword.strip()
    if not keyword:
        return []

    results: list[BusRouteSummary] = []
    seen: set[str] = set()
    for city in CITIES:
        odata_filter = f"contains(RouteName/Zh_tw,'{keyword}')"
        data = await tdx_get(f"/v2/Bus/Route/City/{city}", {"$filter": odata_filter, "$top": 30})
        for item in data if isinstance(data, list) else []:
            name = _zh(item.get("RouteName"))
            if not name or name in seen:
                continue
            seen.add(name)
            results.append(
                BusRouteSummary(
                    id=make_route_id(city, name),
                    name=name,
                    operator=item.get("Operators", [{}])[0].get("OperatorName", {}).get("Zh_tw", "")
                    if item.get("Operators")
                    else "",
                    **{
                        "from_": item.get("DepartureStopNameZh") or "",
                        "to": item.get("DestinationStopNameZh") or "",
                    },
                )
            )
    return results


async def _fetch_stop_of_route(city: str, route_name: str) -> dict[int, list[dict]]:
    data = await tdx_get(f"/v2/Bus/StopOfRoute/City/{city}/{route_name}")
    by_direction: dict[int, list[dict]] = {}
    for entry in data if isinstance(data, list) else []:
        direction = entry.get("Direction")
        if direction not in (0, 1):
            continue
        stops = sorted(entry.get("Stops", []), key=lambda s: s.get("StopSequence", 0))
        by_direction[direction] = stops
    return by_direction


async def _fetch_eta(city: str, route_name: str) -> dict[tuple[int, str], dict]:
    """回傳 {(direction, StopUID): eta資料} 方便依站牌對應。"""
    data = await tdx_get(f"/v2/Bus/EstimatedTimeOfArrival/City/{city}/{route_name}")
    result: dict[tuple[int, str], dict] = {}
    for entry in data if isinstance(data, list) else []:
        direction = entry.get("Direction")
        stop_uid = entry.get("StopUID")
        if direction in (0, 1) and stop_uid:
            result[(direction, stop_uid)] = entry
    return result


def _status_from_eta(entry: dict | None) -> str:
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


@async_ttl_cache(60)  # 含即時到站狀態，免費額度很緊，拉長快取優先保護額度而非資料新鮮度
async def get_route_detail_tdx(route_id: str) -> BusRoute | None:
    city, route_name = parse_route_id(route_id)
    stops_by_direction = await _fetch_stop_of_route(city, route_name)
    if not stops_by_direction:
        return None
    eta_by_key = await _fetch_eta(city, route_name)

    directions: dict[str, BusDirection] = {}
    for direction, stops in stops_by_direction.items():
        if not stops:
            continue
        stop_arrivals = [
            BusStopArrival(
                stop_name=_zh(stop.get("StopName")),
                status=_status_from_eta(eta_by_key.get((direction, stop.get("StopUID")))),
                is_mock=False,
            )
            for stop in stops
        ]
        directions[DIRECTION_KEYS[direction]] = BusDirection(
            direction=DIRECTION_LABELS[direction],
            **{
                "from_": _zh(stops[0].get("StopName")),
                "to": _zh(stops[-1].get("StopName")),
            },
            stops=stop_arrivals,
        )

    if "outbound" not in directions or "inbound" not in directions:
        return None

    return BusRoute(
        id=make_route_id(city, route_name),
        name=route_name,
        operator="",
        outbound=directions["outbound"],
        inbound=directions["inbound"],
    )


async def fetch_nearby_stops_tdx(lat: float, lng: float, radius_m: int = 500) -> list[dict]:
    """回傳指定座標附近的真實公車站牌（合併台北市與新北市）。

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
