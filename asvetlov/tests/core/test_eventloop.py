import collections
import heapq
import socket
import unittest

from unittest.mock import Mock


from core.eventloop import Eventloop
from core.proto import Protocol


class TestEventLoop(unittest.TestCase):
    ADDR = ('127.0.0.1', 6666)

    def create_loop(self, **kwargs):
        el = Eventloop(**kwargs)
        self.addCleanup(el.close)
        return el

    def test_ctor(self):
        el = self.create_loop()
        self.assertTrue(el._running)
        self.assertFalse(el._stopping)
        self.assertEqual({}, el._readers)
        self.assertEqual({}, el._writers)

    def test_listen(self):
        el = self.create_loop()
        proto = None
        class Echo(Protocol):
            def connection_made(self, transport):
                super().connection_made(transport)
                nonlocal proto
                proto = self
            def data_received(self, data):
                self.transport.write(data + b' pong')
            def connection_lost(self, exc):
                super().connection_lost(exc)
                nonlocal proto
                proto = None
        el.listen(self.ADDR, Echo)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(self.ADDR)
        el.run_iter(100)
        self.assertIsNotNone(proto)
        s.sendall(b'ping')
        el.run_iter(100)
        ret = s.recv(1024)
        self.assertEqual(b'ping pong', ret)
        s.sendall(b'ping2')
        el.run_iter(100)
        ret = s.recv(1024)
        self.assertEqual(b'ping2 pong', ret)
        s.close()
        el.run_iter(100)
        self.assertIsNone(proto)



if __name__ == '__main__':
    unitest.main()
