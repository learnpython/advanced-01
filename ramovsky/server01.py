import socket
import signal
from threading import Thread
from argparse import ArgumentParser


def get_options():
    ap = ArgumentParser()
    ap.add_argument('--port', type=int,
        help='Port for connection',
        dest='port', default=9000)
    ap.add_argument('--host',
        help='Host for connection',
        dest='host', default='')
    return ap


class Loop(Thread):

    def __init__(self, srv, conn, addr):
        self.conn = conn
        self.addr = addr
        self.srv = srv
        super().__init__()

    def run(self):
        print('Connected by', self.addr)
        while self.srv.running:
            packet = self.conn.recv(1024)
            print('packet', packet)
            if not packet: break
            cmd, *data = packet.split(b'\n')
            self.conn.sendall(packet)
            if cmd == 'quit':
                self.srv.running = False
        self.conn.close()
            

class Server:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.running = True
        self.clients = []
        
    def run(self):
        while True:
            self.socket.listen(1)
            conn, addr = self.socket.accept()
            cli = Loop(self, conn, addr)
            cli.start()
            self.clients.append(cli)

    def kill(self, signum, frame):
        print('Signal handler called with signal', signum)
        self.running = False


if __name__ == '__main__':
    ap = get_options()
    options = ap.parse_args()
    server = Server(options.host, options.port)
    server.run()
    signal.signal(signal.SIGINT, server.kill)
