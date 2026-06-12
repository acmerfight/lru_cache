# lru_cache

[![CI](https://github.com/acmerfight/lru_cache/actions/workflows/ci.yml/badge.svg)](https://github.com/acmerfight/lru_cache/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/lru_cache.svg)](https://pypi.org/project/lru_cache/)
[![Python versions](https://img.shields.io/pypi/pyversions/lru_cache.svg)](https://pypi.org/project/lru_cache/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Thread-safe LRU cache decorator with optional TTL expiration.

## Installation

```bash
pip install lru_cache
```

## Usage

```python
from lru_cache import LruCache

@LruCache(maxsize=128, timeout=300)
def get_user(user_id: int) -> dict:
    # expensive operation
    return fetch_from_db(user_id)

# Invalidate a specific entry
get_user.invalidate(42)

# Clear all cached entries
get_user.cache_clear()

# Inspect cache state
get_user.cache_info()  # {'size': 10, 'maxsize': 128, 'timeout': 300}
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `maxsize` | `int \| None` | `None` | Maximum number of cached entries. `None` = unbounded. |
| `timeout` | `float \| None` | `None` | TTL in seconds. `None` = entries never expire. |

## Features

- **Thread-safe**: all operations protected by `RLock`
- **TTL support**: entries auto-expire after `timeout` seconds using monotonic clock
- **LRU eviction**: least-recently-used entries evicted when `maxsize` is reached
- **Typed**: full type annotations with `py.typed` marker (PEP 561)
- **Zero dependencies**: pure Python, no external packages

## Migration from 0.x

The import path changed to fix a namespace collision ([#4](https://github.com/acmerfight/lru_cache/issues/4)):

```python
# Old (0.x)
from cache import LruCache

# New (1.x)
from lru_cache import LruCache
```

## License

MIT
