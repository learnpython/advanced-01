import os
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

    def setUp(self):
        self.server = subprocess.Popen(['python3.3', 'command_server.py'])
        self.addCleanup(self.stop_server)
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.connect((self.HOST, self.PORT))

    def stop_server(self):
        os.kill(self.server.pid, signal.SIGUSR1)

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
        self.assertTrue(self.server.poll() is not None)