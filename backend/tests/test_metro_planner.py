"""捷運路線規劃（Dijkstra）邏輯測試，不碰資料庫也不碰 TDX。

測試用小路網：
    綠線 G: G1 - G2 - G3 - G4      （相鄰站每段 MINUTES_PER_STOP 分鐘）
    藍線 B: B1 - G3 - B2           （G3 為 G/B 轉乘站，轉乘 MINUTES_PER_TRANSFER 分鐘）
"""
import pytest

from app.schemas.metro import MetroLine, MetroStation
from app.services import metro_service


def _station(name: str) -> MetroStation:
    return MetroStation(id=name, name=name)


FAKE_LINES = [
    MetroLine(
        id="G",
        name="綠線",
        color="#008659",
        stations=[_station("G1"), _station("G2"), _station("G3"), _station("G4")],
    ),
    MetroLine(
        id="B",
        name="藍線",
        color="#0070bd",
        stations=[_station("B1"), _station("G3"), _station("B2")],
    ),
]


@pytest.fixture(autouse=True)
def _use_fake_lines(monkeypatch):
    async def fake_load_lines():
        return FAKE_LINES

    monkeypatch.setattr(metro_service, "_load_lines", fake_load_lines)
    monkeypatch.setattr(metro_service, "_graph_cache", None)
    yield
    monkeypatch.setattr(metro_service, "_graph_cache", None)


async def test_single_line_no_transfer():
    plan = await metro_service.plan_route("G1", "G4")

    assert plan is not None
    assert plan.transfer_count == 0
    assert plan.total_stop_count == 3
    assert plan.estimated_minutes == 3 * metro_service.MINUTES_PER_STOP
    assert [leg.line_id for leg in plan.legs] == ["G"]
    assert plan.legs[0].board_station == "G1"
    assert plan.legs[0].alight_station == "G4"


async def test_route_with_one_transfer():
    plan = await metro_service.plan_route("G1", "B2")

    assert plan is not None
    assert plan.transfer_count == 1
    assert [leg.line_id for leg in plan.legs] == ["G", "B"]
    # G1->G3 (2 站) 換乘 G3->B2 (1 站)
    assert plan.total_stop_count == 3
    assert plan.legs[0].alight_station == "G3"
    assert plan.legs[1].board_station == "G3"
    expected = 3 * metro_service.MINUTES_PER_STOP + 1 * metro_service.MINUTES_PER_TRANSFER
    assert plan.estimated_minutes == expected


async def test_same_station_returns_none():
    assert await metro_service.plan_route("G2", "G2") is None


async def test_unknown_station_returns_none():
    assert await metro_service.plan_route("G1", "不存在的站") is None
    assert await metro_service.plan_route("也不存在", "G4") is None


async def test_graph_is_cached_between_calls():
    await metro_service.plan_route("G1", "G4")
    first = metro_service._graph_cache
    await metro_service.plan_route("G2", "B2")
    assert metro_service._graph_cache is first  # 同一份 lines 不應重建圖


async def test_search_stations_dedupes_shared_name():
    results = await metro_service.search_stations("G3")
    assert len(results) == 1
    assert results[0]["name"] == "G3"
    assert results[0]["line_ids"] == ["B", "G"]
