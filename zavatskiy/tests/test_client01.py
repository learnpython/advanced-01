import unittest

from server01 import Server01
from client01 import Client01


class TestClient01(unittest.TestCase):

    def setUp(self):
        self.client = Client01()

    def tearDown(self):
        self.client.close()

    def test_connect(self):
        self.client.send('connect', 'HELLO')
        self.assertEqual('connected', self.client.recive()[0])

    def test_ping(self):
        self.client.send('ping')
        self.assertEqual('pong', self.client.recive()[0])

    def test_pingd(self):
        self.client.send('pingd', 'DATA')
        self.assertEqual('pongd', self.client.recive()[0])

    def test_quit(self):
        self.client.send('quit')
        self.assertEqual('ackquit', self.client.recive()[0])

    def test_finish(self):
        self.client.send('finish')
        self.assertEqual('ackfinish', self.client.recive()[0])
        self.client.send('ping')
        self.assertNotEqual('pong', self.client.recive()[0])
