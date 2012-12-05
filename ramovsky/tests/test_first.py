import unittest
import subprocess
from sys import stdout, stderr

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
        self.check_process()

    def check_process(self):
        if self.proc.poll() is not None:
            raise RuntimeError("Process dead")

    def shutdown(self, proc):
        while proc.poll() is None:
            proc.terminate()
            time.sleep(0.1)


class Simple(Base):

    def test_lol(self):
        import socket

        HOST = 'localhost'
        PORT = 9999
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
        s.close()
        print('Received', repr(data))

    
if __name__ == '__main__':
    unittest.main()
