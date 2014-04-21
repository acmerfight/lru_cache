#coding=utf-8
import random
import time
import threading
import unittest
from lru_cache import LruCache


class TesLruCache(unittest.TestCase):

    def test_cache_normal(self):
        a = []
        @LruCache(maxsize=2, timeout=1)
        def foo(num):
            a.append(num)
            return num

        foo(1)
        foo(1)
        self.assertEqual(a, [1])

    def test_cache_none(self):
        a = []
        @LruCache(maxsize=2, timeout=1)
        def foo(num):
            a.append(num)
            return None 

        foo(1)
        foo(1)
        self.assertEqual(a, [1])

    def test_cache_when_timeout(self):
        a = []
        @LruCache(maxsize=2, timeout=1)
        def foo(num):
            a.append(num)
            return num

        foo(2)
        time.sleep(2)
        foo(2)
        self.assertEqual(a, [2, 2])

    def test_cache_when_cache_is_full(self):
        a = []
        @LruCache(maxsize=2, timeout=1)
        def foo(num):
            a.append(num)
            return num

        foo(1)
        foo(2)
        foo(3)
        foo(1)
        self.assertEqual(a, [1, 2, 3, 1])

    def test_cache_with_multi_thread(self):
        a = []
        @LruCache(maxsize=10, timeout=1)
        def foo(num):
            a.append(num)
            return num

        for i in xrange(10):
            threading.Thread(target=foo, args=(i, )).start()

        foo(random.randint(0, 9)) 
        self.assertEqual(set(a), set(range(10)))

    def test_cache_with_multi_thread_two_func(self):
        a = []
        @LruCache(maxsize=10, timeout=1)
        def foo(num):
            a.append(num)
            return num

        b = []
        @LruCache(maxsize=10, timeout=1)
        def bar(num):
            b.append(num)
            return num + 1

        for i in xrange(10):
            threading.Thread(target=foo, args=(i, )).start()
            threading.Thread(target=bar, args=(i, )).start()

        feed = random.randint(0 ,9)
        self.assertEqual(foo(feed), feed)
        self.assertEqual(bar(feed), feed + 1)
        self.assertEqual(set(a), set(range(10)))
        self.assertEqual(set(b), set(range(10)))

if __name__ == "__main__":
    unittest.main()
