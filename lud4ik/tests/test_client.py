import os
import signal
import unittest
import unittest.mock
import subprocess
from sys import stdout, stderr

from command_server import CommandServer
from command_client import CommandClient


class ClientTestCase(unittest.TestCase):

    HOST = ''
    PORT = 50007

    def setUp(self):
        self.server = subprocess.Popen(['python3.3', 'command_server.py'],
                                       stdout=subprocess.PIPE,
                                       stderr=stderr)
        self.client = CommandClient.run_client(self.HOST, self.PORT)
        self.addCleanup(self.stop_server)

    def stop_server(self):
        os.kill(self.server.pid, signal.SIGUSR1)

    def test_connect(self):
        out, _ = self.server.communicate()
        self.client.handle_input('connect')
        import pdb;pdb.set_trace()

    def test_ping(self):
        pass

    def test_pingd(self):
        pass

    def test_quit(self):
        pass

    def test_finish(self):
        pass


