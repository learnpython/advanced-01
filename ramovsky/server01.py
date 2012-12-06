import socket
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


class Server:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        
    def run(self):
        while True:
            self.socket.listen(1)
            conn, addr = self.socket.accept()
            cmd, *data = self.read(conn, addr)
            if cmd == 'quit':
                break

    def read(self, conn, addr):
        print('Connected by', addr)
        while True:
            packet = conn.recv(1024)
            print('packet', packet)
            if not packet: break
            cmd, *data = packet.split(b'\n')
            conn.sendall(packet)
        conn.close()
        return cmd, data            


if __name__ == '__main__':
    ap = get_options()
    options = ap.parse_args()
    server = Server(options.host, options.port)
    server.run()
