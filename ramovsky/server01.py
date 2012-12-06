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
        self.running = True
        super().__init__()

    def run(self):
        print('Connected by', self.addr)
        while self.running:
            if not self.srv.running:
                self.running = False
                self.conn.sendall(b'ackfinish')                
                break
            packet = self.conn.recv(1024)
            if not packet: break
            cmd, *data = packet.split(b'\n')
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
            elif cmd == b'finish':
                self.srv.running = False

        self.conn.close()
            

class Server:

    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((host, port))
        s.settimeout(1.0)
        self.socket = s
        self.running = True
        self.clients = []
        
    def run(self):
        while self.running:
            self.socket.listen(1)
            conn, addr = self.socket.accept()
            cli = Loop(self, conn, addr)
            cli.start()
            self.clients.append(cli)
        print('closing socket')
        self.socket.close()

    def kill(self, signum, frame):
        print('Signal handler called with signal', signum)
        self.running = False


if __name__ == '__main__':
    ap = get_options()
    options = ap.parse_args()
    server = Server(options.host, options.port)
    server.run()
    signal.signal(signal.SIGINT, server.kill)
