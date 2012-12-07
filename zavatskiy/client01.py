import time
import socket

from work.helpers import make_message, parse_message


class Client01:

    def __init__(self, host='127.0.0.1', port=6666):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, command, message=''):
        self.socket.sendall(make_message(command, message))

    def recive(self):
        message = parse_message(self.socket.recv)
        return message

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    client = Client01()
    client.send('connect', 'HELLO')
    ans = client.recive()

    print '> '.join([ans[0], ans[1]])

    while True:
        data = raw_input('pingd> ')
        client.send('pingd', data)

        ans = client.recive()
        if not ans[0]:
            client.close()
        if ans[0] in ['ackquit', 'ackfinish']:
            break

        print '> '.join([ans[0], ans[1]])

    client.close()
