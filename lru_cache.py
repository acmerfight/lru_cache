# coding=utf-8

import time
from threading import RLock
from collections import OrderedDict

from ommited import OmittedType


class LruCache(object):

    def __init__(self, maxsize=None, timeout=None):
        self.maxsize = maxsize
        self.timeout = timeout
        self.Omitted_object = OmittedType()
        if maxsize is not None and timeout is not None:
            self.cache = OrderedDict()
            self.is_full = False
            self.lock = RLock()
        elif maxsize is None and timeout is None:
            self.cache = {}
        elif maxsize is not None and timeout is None:
            self.cache = OrderedDict()
            self.is_full = False
            self.lock = RLock()

    def __call__(self, func):
        if self.timeout is not None and self.maxsize is not None:
            def wrapper(*args, **kwds):
                key = self.make_key(args, kwds)
                with self.lock:
                    result_tuple = self.cache.get(key, self.Omitted_object)
                    if result_tuple is not self.Omitted_object:
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
        elif self.timeout is None and self.maxsize is None:
            def wrapper(*args, **kwds):
                key = self.make_key(args, kwds)
                result = self.cache.get(key, self.Omitted_object)
                if result is self.Omitted_object:
                    result = func(*args, **kwds)
                    self.cache[key] = result
                return result
        elif self.timeout is None and self.maxsize is not None:
            def wrapper(*args, **kwds):
                key = self.make_key(args, kwds)
                with self.lock:
                    result = self.cache.get(key, self.Omitted_object)
                    if result is not self.Omitted_object:
                        del self.cache[key]
                        self.cache[key] = result
                        return result
                result = func(*args, **kwds)
                with self.lock:
                    if key in self.cache:
                        pass
                    elif self.is_full:
                        self.cache.popitem(last=False)
                        self.cache[key] = result
                    else:
                        self.cache[key] = result
                        self.is_full = (len(self.cache) >= self.maxsize)
                return result
        return wrapper

    @staticmethod
    def make_key(args, kwds):
        key = args
        if kwds:
            sorted_items = sorted(kwds.items())
            for item in sorted_items:
                key += item
        return key
