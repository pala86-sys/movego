"""TDX 回傳資料 → 內部格式的純函式轉換測試（不發網路請求）。"""
from app.schemas.metro import MetroStation
from app.services.tdx_bus_service import make_route_id, parse_route_id, status_from_eta
from app.services.tdx_metro_service import (
    _apply_terminus_extensions,
    _split_into_contiguous_segments,
    _status_from_liveboard_entry,
)


def _names(stations):
    return [s.name for s in stations]


class TestApplyTerminusExtensions:
    def test_prepends_when_anchor_is_first(self):
        # TDX 的 R 線陣列是從象山端開始排的
        stations = [MetroStation(id="R02", name="象山"), MetroStation(id="R03", name="台北101/世貿")]
        out = _apply_terminus_extensions("R", stations)
        assert _names(out) == ["廣慈/奉天宮", "象山", "台北101/世貿"]

    def test_appends_when_anchor_is_last(self):
        stations = [MetroStation(id="R03", name="台北101/世貿"), MetroStation(id="R02", name="象山")]
        out = _apply_terminus_extensions("R", stations)
        assert _names(out) == ["台北101/世貿", "象山", "廣慈/奉天宮"]

    def test_noop_when_extension_already_present(self):
        stations = [MetroStation(id="R01", name="廣慈/奉天宮"), MetroStation(id="R02", name="象山")]
        out = _apply_terminus_extensions("R", stations)
        assert _names(out) == ["廣慈/奉天宮", "象山"]

    def test_noop_when_anchor_absent(self):
        stations = [MetroStation(id="R10", name="台北車站")]
        assert _names(_apply_terminus_extensions("R", stations)) == ["台北車站"]

    def test_other_lines_untouched(self):
        stations = [MetroStation(id="BL12", name="市政府"), MetroStation(id="BL11", name="象山")]
        assert _names(_apply_terminus_extensions("BL", stations)) == ["市政府", "象山"]


class TestStatusFromEta:
    def test_none_entry_means_not_departed(self):
        assert status_from_eta(None) == "尚未發車"

    def test_stop_status_one_means_not_departed(self):
        assert status_from_eta({"StopStatus": 1, "EstimateTime": 10}) == "尚未發車"

    def test_missing_estimate_means_not_departed(self):
        assert status_from_eta({"StopStatus": 0}) == "尚未發車"

    def test_arriving_when_within_30_seconds(self):
        assert status_from_eta({"EstimateTime": 20}) == "進站中"

    def test_minutes_are_rounded_and_floored_to_one(self):
        assert status_from_eta({"EstimateTime": 200}) == "約 3 分鐘"
        assert status_from_eta({"EstimateTime": 40}) == "約 1 分鐘"


class TestRouteId:
    def test_round_trip_with_city_prefix(self):
        assert parse_route_id(make_route_id("NewTaipei", "橘20")) == ("NewTaipei", "橘20")

    def test_bare_route_number_defaults_to_taipei(self):
        assert parse_route_id("307") == ("Taipei", "307")

    def test_unknown_prefix_is_treated_as_plain_name(self):
        assert parse_route_id("Foo:bar") == ("Taipei", "Foo:bar")


class TestSplitIntoContiguousSegments:
    def test_contiguous_sequence_stays_one_segment(self):
        raw = [{"Sequence": 1}, {"Sequence": 2}, {"Sequence": 3}]
        assert _split_into_contiguous_segments(raw) == [raw]

    def test_gap_in_sequence_splits_segment(self):
        raw = [
            {"Sequence": 1},
            {"Sequence": 2},
            {"Sequence": 50},
            {"Sequence": 51},
        ]
        segments = _split_into_contiguous_segments(raw)
        assert [len(s) for s in segments] == [2, 2]

    def test_unsorted_input_is_ordered_first(self):
        raw = [{"Sequence": 3}, {"Sequence": 1}, {"Sequence": 2}]
        assert _split_into_contiguous_segments(raw) == [
            [{"Sequence": 1}, {"Sequence": 2}, {"Sequence": 3}]
        ]


class TestStatusFromLiveboardEntry:
    def test_service_status_nonzero_means_not_departed(self):
        assert _status_from_liveboard_entry({"ServiceStatus": 1, "EstimateTime": 3}) == "尚未發車"

    def test_missing_estimate_means_not_departed(self):
        assert _status_from_liveboard_entry({}) == "尚未發車"

    def test_zero_or_negative_estimate_means_arriving(self):
        assert _status_from_liveboard_entry({"EstimateTime": 0}) == "進站中"

    def test_positive_estimate_reports_minutes(self):
        assert _status_from_liveboard_entry({"EstimateTime": 5}) == "約 5 分鐘"
