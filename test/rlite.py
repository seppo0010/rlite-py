# coding=utf-8
from unittest import *
import os.path
import sys

import hirlite


class RliteTest(TestCase):
    def setUp(self):
        self.rlite = hirlite.Rlite()

    def test_none(self):
        self.assertEquals(None, self.rlite.command('get', 'hello'))

    def test_ok(self):
        self.assertEquals(True, self.rlite.command('set', 'hello', 'world'))

    def test_string(self):
        self.rlite.command('set', 'hello', 'world')
        self.assertEquals('world', self.rlite.command('get', 'hello'))

    def test_integer(self):
        self.assertEquals(2, self.rlite.command('lpush', 'list', 'value', 'other value'))

    def test_error(self):
        self.assertIsInstance(self.rlite.command('set', 'key'), hirlite.HirliteError)

    def test_array(self):
        self.rlite.command('rpush', 'mylist', '1', '2', '3')
        self.assertEquals(self.rlite.command('lrange', 'mylist', 0, -1), ['1', '2', '3'])


class PersistentTest(TestCase):
    PATH = 'rlite.rld'
    def setUp(self):
        if os.path.exists(PersistentTest.PATH):
            os.unlink(PersistentTest.PATH)
        self.rlite = hirlite.Rlite(PersistentTest.PATH)

    def tearDown(self):
        if os.path.exists(PersistentTest.PATH):
            os.unlink(PersistentTest.PATH)

    def test_write_close_open(self):
        self.rlite.command('set', 'key', 'value')
        self.rlite = hirlite.Rlite(PersistentTest.PATH)  # close db, open a new one
        self.assertEquals('value', self.rlite.command('get', 'key'))
