lru cahe
=====================

Ba thread-safe lru cache decorator based on **double link list** and **dict** （**OrderedDict**）

### how to install

pip install lru_cache

#### how to use

    from cache import LruCache

    @LruCache(maxsize=2, timeout=1)
    def foo(num):
        return num
