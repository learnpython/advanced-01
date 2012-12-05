import socket
from work.helpers import make_message


class Client01:

    def __init__(self, host='127.0.0.1', port=6666):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, command, message=''):
        self.socket.sendall(make_message(command, message))

    def recive(self):
        buf_size = int(self.socket.recv(4).decode('utf-8').strip())
        return self.socket.recv(buf_size).decode('utf-8').split('\n', 1)

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    client = Client01()
    client.send('connect', 'HELLO')
    print '$', client.recive()[1]

    while True:
        data = raw_input('$ ')
        client.send('pingd', data)
        print client.recive()[1]
        if client.recive()[0] in ['ackquit', 'ackfinish']:
            break

    client.close()
