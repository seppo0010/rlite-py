# coding=utf-8
from unittest import *
import os.path
import sys

import hirlite
import redis


class PatchConnTest(TestCase):
    def setUp(self):
        self.orig_conn = redis.connection.Connection
        hirlite.patch_connection()
        self.assertNotEquals(self.orig_conn, redis.connection.Connection)

    def tearDown(self):
        hirlite.unpatch_connection()
        self.assertEquals(self.orig_conn, redis.connection.Connection)

    def test_basic(self):
        r = redis.StrictRedis()
        r.set('foo', 'bar')
        self.assertEquals(b'bar', r.get('foo'))

    def test_basic_string(self):
        r = redis.StrictRedis(decode_responses=True)
        r.set('foo', 'bar')
        self.assertEquals('bar', r.get('foo'))

    def test_hset_transaction(self):
        r = redis.Redis(decode_responses=True)

        self.assertEquals(0, r.hlen('key'))

        with redis.utils.pipeline(r) as pi:
            pi.hset('key', 'a', '0')
            pi.hset('key', 'b', 1)
            pi.hset('key', 'c', b'2')

        res = r.hgetall('key')
        self.assertEquals({'a': '0', 'b': '1', 'c': '2'}, res)

    def test_from_url(self):
        r = redis.StrictRedis.from_url('redis://localhost/1',
                                       decode_responses=True)

        r.set('foo', 'bar')
        self.assertEquals('bar', r.get('foo'))


    def test_keys(self):
        r = redis.StrictRedis(decode_responses=True)

        r.set('abc', 'foo')
        r.zadd('zset', 0, 'text')
        r.hset('hset', 'foo', 'bar')

        res = r.keys('*')

        self.assertEquals(set(['abc', 'zset', 'hset']), set(res))

    def test_scan(self):
        r = redis.StrictRedis(decode_responses=True)

        r.set('abc', 'foo')
        r.zadd('zset', 0, 'text')
        r.hset('hset', 'foo', 'bar')

        res = list(r.scan_iter(match='*set'))

        self.assertEquals(set(['zset', 'hset']), set(res))


class PatchContextManagerTest(TestCase):
    def test_contextmanager(self):
        orig_conn = redis.connection.Connection

        with hirlite.patch():
            self.assertNotEquals(orig_conn, redis.connection.Connection)

        self.assertEquals(orig_conn, redis.connection.Connection)
