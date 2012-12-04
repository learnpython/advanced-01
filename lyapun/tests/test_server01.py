# coding=utf-8

import signal
import socket
import subprocess
import logging
from unittest import TestCase
from time import sleep

from work.utils import prepare_data_for_sending, parse_recieved_bytes
from work.general import recieve_data_from_socket

logging.disable(logging.CRITICAL)


class ServerTestCase(TestCase):

    def setUp(self):
        self.server = subprocess.Popen(
            ['python', 'server01.py']
        )
        sleep(0.1)

    def tearDown(self):
        if self.server.poll() is None:
            self.server.send_signal(signal.SIGINT)
            self.server.wait()

    def _send_command(self, command):
        HOST = 'localhost'
        PORT = 50007
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((HOST, PORT))
        sock.settimeout(1.0)
        bytes = prepare_data_for_sending(command)
        sock.sendall(bytes)
        data = recieve_data_from_socket(sock)
        sock.close()
        return data

    def test_connect(self):
        data = self._send_command('connect')
        self.assertEqual(b'connected', data)

    def test_ping(self):
        data = self._send_command('ping')
        self.assertEqual(b'pong', data)

    def test_pingd(self):
        data = self._send_command('pingd hello world')
        self.assertEqual(b'pongd\nhello\nworld', data)

    def test_quit(self):
        data = self._send_command('quit')
        self.assertEqual(b'ackquit', data)

    def test_quit_with_data(self):
        data = self._send_command('quit hello world')
        self.assertEqual(b'ackquit\nhello\nworld', data)
        self.assertEqual(
            ('ackquit', 'hello world'), parse_recieved_bytes(data)
        )

    def test_finish(self):
        data = self._send_command('finish')
        self.assertEqual(b'ackfinish', data)
        self.server.wait()
        self.assertEqual(0, self.server.poll())
