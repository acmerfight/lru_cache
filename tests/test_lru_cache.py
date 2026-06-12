from __future__ import annotations

import threading
import time

import pytest

from lru_cache import LruCache


class TestBasicCaching:
    def test_caches_return_value(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def add(a: int, b: int) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        assert add(1, 2) == 3
        assert add(1, 2) == 3
        assert call_count == 1

    def test_caches_none_return(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def returns_none(x: int) -> None:
            nonlocal call_count
            call_count += 1
            return None

        assert returns_none(1) is None
        assert returns_none(1) is None
        assert call_count == 1

    def test_different_args_cached_separately(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        assert identity(1) == 1
        assert identity(2) == 2
        assert call_count == 2

    def test_kwargs_cached(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def greet(name: str = "world") -> str:
            nonlocal call_count
            call_count += 1
            return f"hello {name}"

        assert greet(name="alice") == "hello alice"
        assert greet(name="alice") == "hello alice"
        assert call_count == 1

    def test_args_and_kwargs_distinguish_correctly(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def fn(a: int, b: int = 0) -> int:
            nonlocal call_count
            call_count += 1
            return a + b

        fn(1, 2)
        fn(1, b=2)
        assert call_count == 2


class TestEviction:
    def test_evicts_oldest_when_full(self) -> None:
        call_count = 0

        @LruCache(maxsize=2, timeout=60)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(2)
        identity(3)
        assert call_count == 3

        identity(3)
        assert call_count == 3

        identity(1)
        assert call_count == 4

    def test_access_refreshes_order(self) -> None:
        call_count = 0

        @LruCache(maxsize=2, timeout=60)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)  # cache: [1]
        identity(2)  # cache: [1, 2]
        identity(1)  # access 1, cache: [2, 1]
        identity(3)  # evicts 2, cache: [1, 3]

        # 1 should still be cached (was refreshed)
        identity(1)
        assert call_count == 3

        # 2 was evicted
        identity(2)
        assert call_count == 4


class TestTTLExpiration:
    def test_entry_expires_after_timeout(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=0.1)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        time.sleep(0.15)
        identity(1)
        assert call_count == 2

    def test_entry_valid_before_timeout(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=1.0)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        time.sleep(0.05)
        identity(1)
        assert call_count == 1


class TestUnboundedModes:
    def test_no_maxsize_no_timeout(self) -> None:
        call_count = 0

        @LruCache()
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(1)
        assert call_count == 1

    def test_maxsize_only(self) -> None:
        call_count = 0

        @LruCache(maxsize=2)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(2)
        identity(3)
        identity(1)
        assert call_count == 4

    def test_timeout_only(self) -> None:
        call_count = 0

        @LruCache(timeout=0.1)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(1)
        assert call_count == 1
        time.sleep(0.15)
        identity(1)
        assert call_count == 2


class TestInvalidate:
    def test_invalidate_removes_entry(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        assert call_count == 1
        assert identity.invalidate(1) is True
        identity(1)
        assert call_count == 2

    def test_invalidate_nonexistent_returns_false(self) -> None:
        @LruCache(maxsize=10, timeout=60)
        def identity(x: int) -> int:
            return x

        assert identity.invalidate(999) is False

    def test_cache_clear(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(2)
        identity.cache_clear()
        identity(1)
        identity(2)
        assert call_count == 4


class TestCacheInfo:
    def test_cache_info_reports_state(self) -> None:
        @LruCache(maxsize=5, timeout=10)
        def identity(x: int) -> int:
            return x

        identity(1)
        identity(2)
        info = identity.cache_info()
        assert info == {"size": 2, "maxsize": 5, "timeout": 10}


class TestThreadSafety:
    def test_concurrent_access(self) -> None:
        call_count = 0
        count_lock = threading.Lock()

        @LruCache(maxsize=100, timeout=60)
        def compute(x: int) -> int:
            nonlocal call_count
            with count_lock:
                call_count += 1
            time.sleep(0.01)
            return x * 2

        threads = [threading.Thread(target=compute, args=(i % 10,)) for i in range(50)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert call_count <= 50
        for i in range(10):
            assert compute(i) == i * 2

    def test_concurrent_invalidate(self) -> None:
        @LruCache(maxsize=100, timeout=60)
        def identity(x: int) -> int:
            return x

        for i in range(20):
            identity(i)

        errors: list[Exception] = []

        def invalidate_range(start: int, end: int) -> None:
            try:
                for i in range(start, end):
                    identity.invalidate(i)
            except Exception as e:
                errors.append(e)

        threads = [
            threading.Thread(target=invalidate_range, args=(0, 10)),
            threading.Thread(target=invalidate_range, args=(10, 20)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors


class TestEdgeCases:
    def test_preserves_function_metadata(self) -> None:
        @LruCache(maxsize=10)
        def documented_func(x: int) -> int:
            """A documented function."""
            return x

        assert documented_func.__name__ == "documented_func"
        assert documented_func.__doc__ == "A documented function."

    def test_method_decoration(self) -> None:
        call_count = 0

        class Calculator:
            @LruCache(maxsize=10, timeout=60)
            def double(self, x: int) -> int:
                nonlocal call_count
                call_count += 1
                return x * 2

        calc = Calculator()
        assert calc.double(5) == 10
        assert calc.double(5) == 10
        assert call_count == 1

    def test_maxsize_one(self) -> None:
        call_count = 0

        @LruCache(maxsize=1)
        def identity(x: int) -> int:
            nonlocal call_count
            call_count += 1
            return x

        identity(1)
        identity(2)
        identity(1)
        assert call_count == 3


class TestExceptionBehavior:
    def test_exception_is_not_cached(self) -> None:
        call_count = 0

        @LruCache(maxsize=10, timeout=60)
        def unstable(x: int) -> int:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("transient failure")
            return x

        with pytest.raises(ValueError, match="transient failure"):
            unstable(1)

        assert unstable(1) == 1
        assert call_count == 2

    def test_exception_does_not_corrupt_cache(self) -> None:
        @LruCache(maxsize=2, timeout=60)
        def compute(x: int) -> int:
            if x == 99:
                raise RuntimeError("boom")
            return x * 2

        compute(1)
        compute(2)

        with pytest.raises(RuntimeError):
            compute(99)

        assert compute(1) == 2
        assert compute(2) == 4


class TestRecursion:
    def test_recursive_function_does_not_deadlock(self) -> None:
        @LruCache(maxsize=100)
        def fib(n: int) -> int:
            if n <= 1:
                return n
            return fib(n - 1) + fib(n - 2)

        assert fib(10) == 55
        assert fib(20) == 6765


class TestValidation:
    def test_maxsize_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="maxsize must be a positive integer"):
            LruCache(maxsize=0)

    def test_negative_maxsize_raises(self) -> None:
        with pytest.raises(ValueError, match="maxsize must be a positive integer"):
            LruCache(maxsize=-1)

    def test_negative_timeout_raises(self) -> None:
        with pytest.raises(ValueError, match="timeout must be a positive number"):
            LruCache(timeout=-1)

    def test_zero_timeout_raises(self) -> None:
        with pytest.raises(ValueError, match="timeout must be a positive number"):
            LruCache(timeout=0)
