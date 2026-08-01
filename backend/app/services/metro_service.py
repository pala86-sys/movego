"""捷運資料存取與路線規劃邏輯（不含任何 UI 或 HTTP 細節）。"""
import heapq
from functools import lru_cache

from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import MetroLineModel
from app.schemas.metro import MetroLine, MetroRouteLeg, MetroRoutePlan, MetroStation
from app.services import tdx_metro_service

# 每站平均行駛時間（分鐘），第一版採固定估算值，不涉及即時資料
MINUTES_PER_STOP = 2
MINUTES_PER_TRANSFER = 4

# TDX 的路線／站點資料屬於靜態參考資料（不常變動），呼叫成功後快取在記憶體中，
# 避免每次搜尋/規劃路線都重打一次 TDX API；呼叫失敗則不快取，讓下次請求重試。
_tdx_lines_cache: list[MetroLine] | None = None


@lru_cache
def _load_lines_mock() -> list[MetroLine]:
    """從 SQLite 讀取捷運路線與站點（結果快取，因參考資料為靜態資料）。"""
    with SessionLocal() as db:
        line_models = db.query(MetroLineModel).all()
        return [
            MetroLine(
                id=line.id,
                name=line.name,
                color=line.color,
                stations=[MetroStation(id=s.station_code, name=s.name) for s in line.stations],
            )
            for line in line_models
        ]


async def _load_lines() -> list[MetroLine]:
    global _tdx_lines_cache
    if not get_settings().use_tdx:
        return _load_lines_mock()
    if _tdx_lines_cache is None:
        _tdx_lines_cache = await tdx_metro_service.fetch_lines_tdx()
    return _tdx_lines_cache


async def get_all_lines() -> list[MetroLine]:
    return await _load_lines()


async def get_line(line_id: str) -> MetroLine | None:
    for line in await _load_lines():
        if line.id == line_id:
            return line
    return None


async def search_stations(keyword: str) -> list[dict]:
    """依關鍵字搜尋捷運站，回傳站名與所屬路線（去除重複站名）。"""
    keyword = keyword.strip()
    found: dict[str, set[str]] = {}
    for line in await _load_lines():
        for station in line.stations:
            if keyword and keyword not in station.name:
                continue
            found.setdefault(station.name, set()).add(line.id)
    return [
        {"name": name, "line_ids": sorted(line_ids)}
        for name, line_ids in sorted(found.items())
    ]


async def _build_graph():
    """節點為 (line_id, station_name)，同線相鄰站相連，不同線同站名可轉乘。"""
    lines = await _load_lines()
    graph: dict[tuple[str, str], list[tuple[tuple[str, str], int, bool]]] = {}
    station_to_nodes: dict[str, list[tuple[str, str]]] = {}

    for line in lines:
        names = [s.name for s in line.stations]
        for i, name in enumerate(names):
            node = (line.id, name)
            graph.setdefault(node, [])
            station_to_nodes.setdefault(name, []).append(node)
            if i > 0:
                prev_node = (line.id, names[i - 1])
                graph[node].append((prev_node, 1, False))
                graph.setdefault(prev_node, []).append((node, 1, False))

    for name, nodes in station_to_nodes.items():
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    graph[nodes[i]].append((nodes[j], 0, True))

    return graph, station_to_nodes


async def plan_route(from_station: str, to_station: str) -> MetroRoutePlan | None:
    """以最少轉乘、其次最少站數為原則規劃路線。"""
    graph, station_to_nodes = await _build_graph()

    if from_station not in station_to_nodes or to_station not in station_to_nodes:
        return None
    if from_station == to_station:
        return None

    starts = station_to_nodes[from_station]
    targets = set(station_to_nodes[to_station])

    # 成本以 (轉乘次數, 站數) 排序，用 transfers*10000 + stops 編碼成單一整數
    dist: dict[tuple[str, str], int] = {}
    prev: dict[tuple[str, str], tuple[tuple[str, str], bool] | None] = {}
    pq: list[tuple[int, tuple[str, str]]] = []

    for s in starts:
        dist[s] = 0
        prev[s] = None
        heapq.heappush(pq, (0, s))

    best_target = None
    best_cost = None

    while pq:
        cost, node = heapq.heappop(pq)
        if cost > dist.get(node, float("inf")):
            continue
        if node in targets:
            best_target = node
            best_cost = cost
            break
        for neighbor, stop_cost, is_transfer in graph.get(node, []):
            step = 10000 if is_transfer else stop_cost
            new_cost = cost + step
            if new_cost < dist.get(neighbor, float("inf")):
                dist[neighbor] = new_cost
                prev[neighbor] = (node, is_transfer)
                heapq.heappush(pq, (new_cost, neighbor))

    if best_target is None:
        return None

    # 回溯路徑
    path: list[tuple[tuple[str, str], bool]] = []
    node = best_target
    while prev[node] is not None:
        parent, is_transfer = prev[node]
        path.append((node, is_transfer))
        node = parent
    path.reverse()

    lines_by_id = {line.id: line for line in await _load_lines()}

    legs: list[MetroRouteLeg] = []
    current_line = starts[0][0]
    board_station = from_station
    stop_count = 0

    for (line_id, station_name), is_transfer in path:
        if is_transfer:
            legs.append(
                MetroRouteLeg(
                    line_id=current_line,
                    line_name=lines_by_id[current_line].name,
                    line_color=lines_by_id[current_line].color,
                    board_station=board_station,
                    alight_station=station_name,
                    stop_count=stop_count,
                )
            )
            current_line = line_id
            board_station = station_name
            stop_count = 0
        else:
            stop_count += 1

    legs.append(
        MetroRouteLeg(
            line_id=current_line,
            line_name=lines_by_id[current_line].name,
            line_color=lines_by_id[current_line].color,
            board_station=board_station,
            alight_station=to_station,
            stop_count=stop_count,
        )
    )

    total_stops = sum(leg.stop_count for leg in legs)
    transfer_count = len(legs) - 1
    estimated_minutes = total_stops * MINUTES_PER_STOP + transfer_count * MINUTES_PER_TRANSFER

    return MetroRoutePlan(
        from_station=from_station,
        to_station=to_station,
        legs=legs,
        transfer_count=transfer_count,
        total_stop_count=total_stops,
        estimated_minutes=estimated_minutes,
    )


async def get_liveboard(station_name: str) -> list[dict] | None:
    """回傳即時到站看板；只有 USE_TDX=true 時才有資料，否則回傳 None 表示此功能未啟用。"""
    if not get_settings().use_tdx:
        return None
    return await tdx_metro_service.fetch_liveboard_tdx(station_name)
