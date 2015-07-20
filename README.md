lru cahe
=====================

Thread-safe lru cache decorator based on **double link list** and **dict** （**OrderedDict**）

### how to install

pip install lru_cache

#### how to use

    from cache import LruCache

    # maxsize the max number of cache object
    # timeout the max time(second) cache object stay
    @LruCache(maxsize=2, timeout=1)
    def foo(num):
        return num

    # invalidate cache
    foo.invalidate(num)

#### hint

* timeout is not updated in real time

* LruCache doesn't support unhashable obejct
