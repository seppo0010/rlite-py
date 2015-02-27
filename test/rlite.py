# coding=utf-8
from unittest import *
import hirlite
import sys


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
