# coding=utf-8
from unittest import *
import os.path
import sys

import hirlite


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
        self.assertEquals(b'value', self.rlite.command('get', 'key'))

    def test_pubsub(self):
        self.assertEquals(['subscribe', 'channel', 1L], self.rlite.command('subscribe', 'channel', 'channel2'))
        self.assertEquals(['subscribe', 'channel2', 2L], self.rlite.command('__rlite_poll'))
        rlite2 = hirlite.Rlite(PersistentTest.PATH)
        self.assertEquals(1L, rlite2.command('publish', 'channel', 'hello world'))
        r = self.rlite.command('__rlite_poll', '0')
        self.assertEquals(r, ['message', 'channel', 'hello world'])
        self.assertEquals(['unsubscribe', 'channel2', 1L], self.rlite.command('unsubscribe'))
        self.assertEquals(['unsubscribe', 'channel', 0L], self.rlite.command('__rlite_poll'))
        self.assertEquals(None, self.rlite.command('__rlite_poll'))
