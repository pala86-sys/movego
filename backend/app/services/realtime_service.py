"""到站狀態模擬邏輯。

第一版尚未串接 TDX，所有到站時間皆為「模擬資料」，僅供介面展示使用，
每個站牌+路線+方向的組合會得到穩定（不會每次整頁重整都亂跳）但會隨時間緩慢變化的模擬狀態。
"""
import hashlib
import time


def _stable_seed(*parts: str) -> int:
    key = "|".join(parts).encode("utf-8")
    return int(hashlib.md5(key).hexdigest(), 16)


def mock_arrival_status(route_id: str, direction: str, stop_name: str) -> str:
    """回傳「進站中」「約 X 分鐘」「尚未發車」其中一種模擬狀態。"""
    # 每 30 秒變化一次時間桶，讓資料看起來像是有在跑動，但同一時間桶內結果一致
    time_bucket = int(time.time() // 30)
    seed = _stable_seed(route_id, direction, stop_name, str(time_bucket))
    bucket = seed % 10

    if bucket == 0:
        return "進站中"
    if bucket <= 6:
        minutes = (seed // 10) % 20 + 1
        return f"約 {minutes} 分鐘"
    return "尚未發車"
