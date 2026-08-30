"""極簡的非同步函式短時效快取，用來降低對 TDX 免費額度（5 次/分鐘）的消耗。

- 只快取「成功」的結果；呼叫失敗（拋例外，例如 TDX 額度用完）不會被快取，
  下一次請求仍會重新嘗試，不會讓使用者卡在一個過期的錯誤狀態。
- 同一個 key 若已有一個呼叫在進行中，後到的請求會共用那個結果，不會各自
  再打一次 TDX（避免冷快取時的併發請求把免費額度乘上好幾倍）。
- 每次寫入後順手清掉已過期的項目，避免長時間執行下 key 無限累積。
"""
import asyncio
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


def async_ttl_cache(ttl_seconds: float) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        cache: dict[tuple, tuple[float, T]] = {}
        inflight: dict[tuple, "asyncio.Future[T]"] = {}

        @wraps(fn)
        async def wrapper(*args, **kwargs) -> T:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            cached = cache.get(key)
            if cached is not None and now - cached[0] < ttl_seconds:
                return cached[1]

            existing = inflight.get(key)
            if existing is not None:
                return await existing

            task = asyncio.ensure_future(fn(*args, **kwargs))
            inflight[key] = task
            try:
                value = await task
            finally:
                inflight.pop(key, None)

            cache[key] = (time.time(), value)
            cutoff = time.time() - ttl_seconds
            for stale_key in [k for k, (ts, _) in cache.items() if ts < cutoff]:
                cache.pop(stale_key, None)
            return value

        return wrapper

    return decorator
