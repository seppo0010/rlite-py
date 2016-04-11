# coding=utf-8
from unittest import *
import os.path
import sys

import hirlite


class RliteTest(TestCase):
    def setUp(self):
        self.rlite = hirlite.Rlite()

    def test_encoding(self):
        snowman = b'\xe2\x98\x83'
        self.assertEquals(snowman, self.rlite.command('ping', snowman))
        self.rlite = hirlite.Rlite(encoding='utf8')
        self.assertEquals(snowman.decode('utf-8'), self.rlite.command('ping', snowman))

    def test_none(self):
        self.assertEquals(None, self.rlite.command('get', 'hello'))

    def test_ok(self):
        self.assertEquals(True, self.rlite.command('set', 'hello', 'world'))

    def test_string(self):
        self.rlite.command('set', 'hello', 'world')
        self.assertEquals(b'world', self.rlite.command('get', 'hello'))

    def test_integer(self):
        self.assertEquals(2, self.rlite.command('lpush', 'list', 'value', 'other value'))

    def test_error(self):
        result = self.rlite.command('set', 'key')
        if hasattr(self, 'assertIsInstance'):
            self.assertIsInstance(result, hirlite.HirliteError)
        else:
            self.assertTrue(isinstance(result, hirlite.HirliteError))

    def test_array(self):
        self.rlite.command('rpush', 'mylist', '1', '2', '3')
        self.assertEquals(self.rlite.command('lrange', 'mylist', '0', '-1'), [b'1', b'2', b'3'])

    def test_getattr(self):
        self.assertTrue(self.rlite.set('x', b'y'))
        self.assertEqual(self.rlite.get('x'), b'y')
        self.assertEqual(self.rlite.delete('x'), 1)
        self.assertEqual(self.rlite.exists('x'), 0)

    def test_getattr_err(self):
        command = 'invalidcommand'
        res = getattr(self.rlite, command)()
        self.assertTrue(isinstance(res, hirlite.HirliteError))
        self.assertEqual(res.args[0], "unknown command '%s'" % command)
