import socket
import signal
from argparse import ArgumentParser


def get_options():
    ap = ArgumentParser()
    ap.add_argument('--port', type=int,
        help='Port for connection',
        dest='port', default=9000)
    ap.add_argument('--host',
        help='Host for connection',
        dest='host', default='127.0.0.1')
    return ap


class Client:

    def __init__(self, host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.settimeout(.1)
        s.sendall(b'connect')
        data = s.recv(1024)
        print('srv: ', data)
        self.socket = s
        self.running = True

    def run(self):
        while self.running:
            user_input = input('cli: ')
            self.socket.sendall(user_input.encode('ascii'))
            data = self.socket.recv(1024)
            print('srv: ', data)
            cmd, *data = data.split(b' ')
            if cmd in [b'ackquit', b'ackfinish']:
                self.running = False

        print('By')
        self.socket.close()

    def kill(self, signum, frame):
        self.running = False


if __name__ == '__main__':
    ap = get_options()
    options = ap.parse_args()
    cli = Client(options.host, options.port)
    signal.signal(signal.SIGINT, cli.kill)
    try:
        cli.run()
    except KeyboardInterrupt:
        pass
