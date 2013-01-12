import socket

from core import msg


class Client:
    def __init__(self):
        self.fd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, addr):
        self.fd.connect(addr)

    def close(self):
        self.fd.close()

    def loop(self):
        pass
