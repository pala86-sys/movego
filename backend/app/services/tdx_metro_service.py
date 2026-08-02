"""TDX 台北捷運（TRTC）資料轉換：路線／站點清單、即時到站看板。

欄位名稱依 TDX Basic API v2 Rail/Metro 資料集；使用 .get() 防呆，避免欄位缺漏讓整支 API 掛掉。
"""
from app.schemas.metro import MetroLine, MetroStation
from app.services.tdx_client import tdx_get
from app.services.ttl_cache import async_ttl_cache

# 台北捷運本體在 TRTC，環狀線由新北捷運公司營運，掛在 NTMC 底下（TDX 官方 RailSystem 代碼）
RAIL_SYSTEMS = ["TRTC", "NTMC"]

# TDX 的 LineID 沿用官方路線代碼（與我們原本手動維護的顏色一致），找不到時使用預設灰色
LINE_COLORS = {
    "R": "#e3002c",
    "G": "#008659",
    "BL": "#0070bd",
    "O": "#f8b61c",
    "BR": "#c48c31",
    "Y": "#fdb827",
}
DEFAULT_COLOR = "#8a8a8a"

# StationOfLine 端點不會回傳路線中文名稱（只有 LineID），因此另外用靜態對照表補上
LINE_NAMES = {
    "R": "淡水信義線",
    "G": "松山新店線",
    "BL": "板南線",
    "O": "中和新蘆線",
    "BR": "文湖線",
    "Y": "環狀線",
}

# TDX StationOfLine 對於有分岔的路線（目前已知只有中和新蘆線），Sequence 編號會跳號
# （例如 1~21 是主線＋迴龍支線，50~54 是另一條蘆洲支線），代表這兩段不是實際相鄰的站，
# 但站陣列裡的 Sequence 跳號段落並不會告訴我們該接回主線的哪一站，所以用這張表手動標記
# 「跳號後那一段的第一站」實際上應該接在主線的哪一站之後。
KNOWN_BRANCH_ATTACHMENTS: dict[tuple[str, str], str] = {
    ("O", "三重國小"): "大橋頭",
}


def _zh(field: dict | None) -> str:
    if not field:
        return ""
    return field.get("Zh_tw") or field.get("Zh_TW") or ""


def _split_into_contiguous_segments(stations_raw: list[dict]) -> list[list[dict]]:
    """依 Sequence 是否連續切段，避免把分岔路線裡不相鄰的站誤判成相鄰。"""
    ordered = sorted(stations_raw, key=lambda s: s.get("Sequence", 0))
    segments: list[list[dict]] = []
    prev_seq: int | None = None
    for station in ordered:
        seq = station.get("Sequence", 0)
        if prev_seq is None or seq != prev_seq + 1:
            segments.append([])
        segments[-1].append(station)
        prev_seq = seq
    return segments


async def fetch_lines_tdx() -> list[MetroLine]:
    lines: list[MetroLine] = []
    for rail_system in RAIL_SYSTEMS:
        data = await tdx_get(f"/v2/Rail/Metro/StationOfLine/{rail_system}")
        for entry in data if isinstance(data, list) else []:
            line_id = entry.get("LineID", "")
            line_name = LINE_NAMES.get(line_id, line_id)
            line_color = LINE_COLORS.get(line_id, DEFAULT_COLOR)

            segments = _split_into_contiguous_segments(entry.get("Stations", []))
            segments = [seg for seg in segments if seg]
            if not segments:
                continue

            main_stations = [
                MetroStation(id=s.get("StationID", ""), name=_zh(s.get("StationName")))
                for s in segments[0]
                if _zh(s.get("StationName"))
            ]
            if not main_stations:
                continue
            lines.append(MetroLine(id=line_id, name=line_name, color=line_color, stations=main_stations))

            for i, segment in enumerate(segments[1:], start=1):
                branch_names = [
                    MetroStation(id=s.get("StationID", ""), name=_zh(s.get("StationName")))
                    for s in segment
                    if _zh(s.get("StationName"))
                ]
                if not branch_names:
                    continue
                attach_to = KNOWN_BRANCH_ATTACHMENTS.get((line_id, branch_names[0].name))
                if attach_to:
                    branch_names.insert(0, MetroStation(id="", name=attach_to))
                lines.append(
                    MetroLine(
                        id=f"{line_id}-seg{i}",
                        name=f"{line_name}（支線）",
                        color=line_color,
                        stations=branch_names,
                    )
                )
    return lines


def _status_from_liveboard_entry(entry: dict) -> str:
    service_status = entry.get("ServiceStatus")
    if service_status not in (None, 0):
        return "尚未發車"
    estimate_minutes = entry.get("EstimateTime")
    if estimate_minutes is None:
        return "尚未發車"
    if estimate_minutes <= 0:
        return "進站中"
    return f"約 {estimate_minutes} 分鐘"


@async_ttl_cache(60)  # 即時看板快取，免費額度很緊，拉長快取優先保護額度而非資料新鮮度
async def fetch_liveboard_tdx(station_name: str) -> list[dict]:
    """回傳指定站名的即時列車看板：[{destination, status}]。"""
    odata_filter = f"StationName/Zh_tw eq '{station_name}'"
    board = []
    for rail_system in RAIL_SYSTEMS:
        data = await tdx_get(f"/v2/Rail/Metro/LiveBoard/{rail_system}", {"$filter": odata_filter})
        for entry in data if isinstance(data, list) else []:
            destination = _zh(entry.get("DestinationStationName")) or entry.get("TripHeadSign", "")
            board.append({"destination": destination, "status": _status_from_liveboard_entry(entry)})
    return board


async def fetch_nearby_stations_tdx(lat: float, lng: float, radius_m: int = 500) -> list[dict]:
    """回傳指定座標附近的真實捷運站，同一站名（多線交會）會合併成一筆。"""
    by_name: dict[str, dict] = {}
    for rail_system in RAIL_SYSTEMS:
        data = await tdx_get(
            f"/v2/Rail/Metro/Station/{rail_system}",
            {"$spatialFilter": f"nearby({lat},{lng},{radius_m})", "$top": 30},
        )
        for item in data if isinstance(data, list) else []:
            name = _zh(item.get("StationName"))
            station_id = item.get("StationID", "")
            if not name:
                continue
            line_id = station_id.rstrip("0123456789")  # 例如 "BL12" -> "BL"，粗略取出路線代碼
            position = item.get("StationPosition") or {}
            if name not in by_name:
                by_name[name] = {
                    "id": item.get("StationUID", station_id),
                    "name": name,
                    "type": "metro",
                    "lat": position.get("PositionLat", lat),
                    "lng": position.get("PositionLon", lng),
                    "lines": [],
                    "routes": [],
                }
            if line_id and line_id not in by_name[name]["lines"]:
                by_name[name]["lines"].append(line_id)
    return list(by_name.values())
