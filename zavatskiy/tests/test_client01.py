import unittest
from server01 import Server01
from client01 import Client01


class TestClient01(unittest.TestCase):

    def setUp(self):
        self.client = Client01()

    def test_connect(self):
        self.client.send('connect', 'HELLO')
        self.assertEqual(b'connected', self.client.recive()[0])

    def test_ping(self):
        self.client.send('ping')
        self.assertEqual(b'pong', self.client.recive()[0])

    def test_pingd(self):
        self.client.send('pingd', 'DATA')
        self.assertEqual(b'pongd', self.client.recive()[0])

    def test_quit(self):
        self.client.send('quit')
        self.assertEqual(b'ackquit', self.client.recive()[0])

    def test_finish(self):
        self.client.send('finish')
        self.assertEqual(b'ackfinish', self.client.recive()[0])

    def tearDown(self):
        self.client.close()
