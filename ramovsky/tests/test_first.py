import time
import signal
import unittest
import subprocess
import socket
from sys import stdout, stderr

HOST = 'localhost'
PORT = 9991


class Base(unittest.TestCase):

    def setUp(self):
        null = open('/dev/null', 'a')
        self.addCleanup(null.close)

        commandline = [
            'python3',
            '-m',
            'server01',
            '--port=9991',
            ]
        self.proc = subprocess.Popen(commandline,
            stdout=stdout, stderr=stderr)
        time.sleep(.5)

    def tearDown(self):
        if self.proc.poll() is None:
            self.proc.send_signal(signal.SIGINT)
            self.proc.wait()


class Simple(Base):

    def test_single(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))

        s.sendall(b'connect')
        data = s.recv(1024)
        self.assertEqual(b'connected', data)

        s.sendall(b'ping')
        data = s.recv(1024)
        self.assertEqual(b'pong', data)

        s.sendall(b'pingd')
        data = s.recv(1024)
        self.assertEqual(b'pongd data not send', data)

        s.sendall(b'pingd\ndddd')
        data = s.recv(1024)
        self.assertEqual(b'pongd dddd', data)

        s.sendall(b'quit')
        data = s.recv(1024)
        self.assertEqual(b'ackquit', data)

        s.close()

    def test_two(self):
        s1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s1.connect((HOST, PORT))
        s2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s2.connect((HOST, PORT))

        s1.sendall(b'connect')
        data = s1.recv(1024)
        self.assertEqual(b'connected', data)

        s2.sendall(b'connect')
        data = s2.recv(1024)
        self.assertEqual(b'connected', data)

        s1.sendall(b'finish')
        data = s1.recv(1024)
        self.assertEqual(b'ackfinish', data)

        data = s2.recv(1024)
        self.assertEqual(b'ackfinish', data)

        s1.close()
        s2.close()


if __name__ == '__main__':
    unittest.main()
