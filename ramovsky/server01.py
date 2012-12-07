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
        dest='host', default='0.0.0.0')
    return ap


class Loop(Thread):

    def __init__(self, srv, conn, addr):
        self.conn = conn
        self.addr = addr
        self.srv = srv
        self.running = True
        super().__init__()

    def run(self):
        print('Connected by', self.addr)
        while self.running:
            if not self.srv.running:
                self.conn.sendall(b'ackfinish')
                self.running = False
                break
            try:
                packet = self.conn.recv(1024)
            except socket.timeout:
                continue
            if not packet: continue
            cmd, *data = packet.split(b' ')
            print('got command', cmd, data)
            if cmd == b'connect':
                self.conn.sendall(b'connected')
            elif cmd == b'ping':
                self.conn.sendall(b'pong')
            elif cmd == b'pingd':
                if not data:
                    data = b'data not send'
                else:
                    data = b' '.join(data)
                self.conn.sendall(b'pongd '+data)
            elif cmd == b'quit':
                self.conn.sendall(b'ackquit')
                self.running = False
                break
            elif cmd == b'finish':
                self.srv.running = False
            else:
                self.conn.sendall(b'unknown command')

        self.conn.close()


class Server:

    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))
        s.settimeout(1.0)
        self.socket = s
        self.running = True
        self.clients = {}
        print('Started server {}:{}'.format(host, port))

    def run(self):
        while self.running:
            self.socket.listen(1)
            try:
                conn, addr = self.socket.accept()
                conn.settimeout(.1)
                cli = Loop(self, conn, addr)
                cli.start()
                self.clients[addr] = cli
            except (socket.error, socket.timeout):
                pass

        for c in self.clients.values():
            c.join()
        self.socket.close()

    def kill(self, signum, frame):
        print('Signal handler called with signal', signum)
        self.running = False


if __name__ == '__main__':
    ap = get_options()
    options = ap.parse_args()
    server = Server(options.host, options.port)
    signal.signal(signal.SIGINT, server.kill)
    server.run()
