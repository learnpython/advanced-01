import time
import unittest
import subprocess
import socket
from sys import stdout, stderr

HOST = 'localhost'
PORT = 9999


class Base(unittest.TestCase):

    def setUp(self):
        null = open('/dev/null', 'a')
        self.addCleanup(null.close)

        commandline = [
            'python3',
            '-m',
            'server01',
            '--port=9999',
            ]
        self.proc = subprocess.Popen(commandline,
            stdout=stdout, stderr=stderr)
        self.addCleanup(self.shutdown)
        time.sleep(.5)

    def check_process(self):
        if self.proc.poll() is not None:
            raise RuntimeError("Process dead")

    def shutdown(self):
        while self.proc.poll() is None:
            self.proc.terminate()
            time.sleep(.1)


class Simple(Base):

    def test_lol(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        print('Received', repr(data))
        s.sendall(b'quit')
        data = s.recv(1024)
        print('Received', repr(data))

        s.close()

    
if __name__ == '__main__':
    unittest.main()
