"""極簡的非同步函式短時效快取，用來降低對 TDX 免費額度（5 次/分鐘）的消耗。

只快取「成功」的結果；呼叫失敗（拋例外，例如 TDX 額度用完）不會被快取，
下一次請求仍會重新嘗試，不會讓使用者卡在一個過期的錯誤狀態。
"""
import time
from collections.abc import Awaitable, Callable
from functools import wraps
from typing import TypeVar

T = TypeVar("T")


def async_ttl_cache(ttl_seconds: float) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    def decorator(fn: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        cache: dict[tuple, tuple[float, T]] = {}

        @wraps(fn)
        async def wrapper(*args, **kwargs) -> T:
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            cached = cache.get(key)
            if cached is not None and now - cached[0] < ttl_seconds:
                return cached[1]

            value = await fn(*args, **kwargs)
            cache[key] = (now, value)
            return value

        return wrapper

    return decorator
