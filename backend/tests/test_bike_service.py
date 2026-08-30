"""YouBike 即時車況 → 狀態字串的純函式轉換測試（不發網路請求）。"""
from app.services.tdx_bike_service import _status_from_availability


def test_none_entry_has_no_data():
    assert _status_from_availability(None) == ("無即時資料", None, None, None, None)


def test_normal_service_with_general_and_electric_split():
    entry = {
        "ServiceStatus": 1,
        "AvailableRentBikes": 12,
        "AvailableReturnBikes": 8,
        "AvailableRentBikesDetail": {"GeneralBikes": 9, "ElectricBikes": 3},
    }
    assert _status_from_availability(entry) == ("正常", 12, 9, 3, 8)


def test_missing_detail_keeps_total_but_no_split():
    entry = {"ServiceStatus": 1, "AvailableRentBikes": 5, "AvailableReturnBikes": 10}
    assert _status_from_availability(entry) == ("正常", 5, None, None, 10)


def test_service_status_two_is_suspended():
    entry = {"ServiceStatus": 2, "AvailableRentBikes": 0, "AvailableReturnBikes": 0}
    assert _status_from_availability(entry)[0] == "暫停營運"


def test_service_status_zero_is_stopped():
    assert _status_from_availability({"ServiceStatus": 0})[0] == "停止營運"


def test_unknown_service_status_defaults_to_normal():
    assert _status_from_availability({"AvailableRentBikes": 3})[0] == "正常"
