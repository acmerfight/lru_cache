# Changelog

## 1.0.0 (2026-06-11)

### Breaking Changes

- **Renamed import path**: use `from lru_cache import LruCache` instead of `from cache import LruCache`.
  This fixes the long-standing namespace collision issue (#4).
- Dropped Python 2 and Python < 3.9 support.
- `invalidate()` now returns `bool` indicating whether an entry was removed.

### Added

- `cache_clear()` method to remove all entries at once.
- `cache_info()` method returning current cache state.
- Type annotations and `py.typed` marker (PEP 561).
- Parameter validation: `maxsize` and `timeout` must be positive when provided.

### Fixed

- Key collision between positional and keyword arguments (`f(1, 2)` vs `f(1, b=2)` are now distinct).
- Use `time.monotonic()` instead of `time.time()` to prevent clock-skew issues.
- Unified code path eliminates duplicated logic for different parameter combinations.

### Improved

- Modern packaging with `pyproject.toml` and `hatchling`.
- CI with GitHub Actions testing Python 3.9–3.13.
- 100% test branch coverage enforced.
- Linting with ruff, type checking with mypy strict mode.
