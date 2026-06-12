from __future__ import annotations

import functools
import time
from collections import OrderedDict
from threading import RLock
from typing import Any, Callable, TypeVar

_SENTINEL = object()

F = TypeVar("F", bound=Callable[..., Any])


def _make_key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> tuple[Any, ...]:
    key: tuple[Any, ...] = args
    if kwargs:
        key += (_SENTINEL,)
        for item in sorted(kwargs.items()):
            key += item
    return key


class LruCache:
    """Thread-safe LRU cache decorator with optional TTL expiration.

    Parameters
    ----------
    maxsize:
        Maximum number of entries. ``None`` means unbounded.
    timeout:
        Time-to-live in seconds. ``None`` means entries never expire.
    """

    __slots__ = ("maxsize", "timeout")

    def __init__(
        self,
        maxsize: int | None = None,
        timeout: float | None = None,
    ) -> None:
        if maxsize is not None and maxsize < 1:
            raise ValueError("maxsize must be a positive integer")
        if timeout is not None and timeout <= 0:
            raise ValueError("timeout must be a positive number")
        self.maxsize = maxsize
        self.timeout = timeout

    def __call__(self, func: F) -> F:
        lock = RLock()
        cache: OrderedDict[tuple[Any, ...], tuple[Any, float]] = OrderedDict()
        maxsize = self.maxsize
        timeout = self.timeout

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            key = _make_key(args, kwargs)
            now = time.monotonic()

            with lock:
                if key in cache:
                    value, ts = cache[key]
                    if timeout is None or (now - ts) <= timeout:
                        cache.move_to_end(key)
                        return value
                    else:
                        del cache[key]

            result = func(*args, **kwargs)

            with lock:
                if key in cache:
                    cache.move_to_end(key)
                    cache[key] = (result, time.monotonic())
                else:
                    cache[key] = (result, time.monotonic())
                    if maxsize is not None and len(cache) > maxsize:
                        cache.popitem(last=False)

            return result

        def cache_invalidate(*args: Any, **kwargs: Any) -> bool:
            key = _make_key(args, kwargs)
            with lock:
                if key in cache:
                    del cache[key]
                    return True
                return False

        def cache_clear() -> None:
            with lock:
                cache.clear()

        def cache_info() -> dict[str, Any]:
            with lock:
                return {
                    "size": len(cache),
                    "maxsize": maxsize,
                    "timeout": timeout,
                }

        wrapper.invalidate = cache_invalidate  # type: ignore[attr-defined]
        wrapper.cache_clear = cache_clear  # type: ignore[attr-defined]
        wrapper.cache_info = cache_info  # type: ignore[attr-defined]
        wrapper.cache = cache  # type: ignore[attr-defined]

        return wrapper  # type: ignore[return-value]
