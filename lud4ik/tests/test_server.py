import os
import os.path
import time
import socket
import signal
import unittest
import subprocess

from command_server import CommandServer
from command_client import CommandClient
from work.utils import format_reply, get_msg

class ServerTestCase(unittest.TestCase):

    HOST = ''
    PORT = 50007
    PID_FILE = 'server.pid'

    def setUp(self):
        self.server = subprocess.Popen(['python3.3', 'command_server.py'])
        self.addCleanup(self.stop_server)
        while True:
            if os.path.exists(self.PID_FILE):
                time.sleep(0.2)
                break
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.HOST, self.PORT))

    def stop_server(self):
        if self.server.poll() is None:
            os.kill(self.server.pid, signal.SIGINT)

    def test_connect(self):
        self.socket.sendall(format_reply('connect'))
        reply = get_msg(self.socket).decode('utf-8')
        self.assertTrue(reply.startswith('connected'))
        self.assertTrue(reply.split('\n')[-1].startswith('session'))

    def test_ping(self):
        self.socket.sendall(format_reply('ping'))
        reply = get_msg(self.socket).decode('utf-8')
        self.assertTrue(reply == 'pong')

    def test_pingd(self):
        self.socket.sendall(format_reply('pingd\ntest'))
        reply = get_msg(self.socket).decode('utf-8').split('\n')
        self.assertEqual(reply[0], 'pongd')
        self.assertEqual(reply[1], 'test')

    def test_quit(self):
        self.socket.sendall(format_reply('quit'))
        reply = get_msg(self.socket).decode('utf-8')
        self.assertTrue(reply.startswith('ackquit'))

    def test_finish(self):
        self.socket.sendall(format_reply('finish'))
        reply = get_msg(self.socket).decode('utf-8')
        self.assertTrue(reply.startswith('ackfinish'))
        while True:
            if not os.path.exists(self.PID_FILE):
                time.sleep(0.1)
                break
        self.assertTrue(self.server.poll() is not None)
