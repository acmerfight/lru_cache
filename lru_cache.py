#coding=utf-8

import time
from threading import RLock
from collections import OrderedDict


class LruCache(object):

    def __init__(self, maxsize=100, timeout=3600):
        self.maxsize = maxsize
        self.timeout = timeout
        self.cache = OrderedDict()
        self.is_full = False
        self.lock = RLock()

    def __call__(self, func):

        def wrapper(*args, **kwds):
            key = self.make_key(args, kwds)
            with self.lock:
                result_tuple = self.cache.get(key)
                if result_tuple is not None:
                    result, old_time = result_tuple
                    if int(time.time()) - old_time <= self.timeout:
                        del self.cache[key]
                        self.cache[key] = result_tuple
                        return result
                    else:
                        del self.cache[key]
                        self.is_full = (len(self.cache) >= self.maxsize) 
            result_tuple = func(*args, **kwds), int(time.time())
            with self.lock:
                if key in self.cache:
                    pass
                elif self.is_full:
                    self.cache.popitem(last=False)
                    self.cache[key] = result_tuple
                else:
                    self.cache[key] = result_tuple
                    self.is_full = (len(self.cache) >= self.maxsize) 
            return result_tuple[0]
        return wrapper

    @staticmethod
    def make_key(args, kwds):
        key = args
        if kwds:
            sorted_items = sorted(kwds.items())
            for item in sorted_items:
                key += item
        return key
