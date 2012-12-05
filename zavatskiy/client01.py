import socket


class Client01:

    def __init__(self, host='127.0.0.1', port=6666):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self):
        self.socket.sendall(b'Hello')

    def recive(self):
        data = self.socket.recv(1024)

    def close(self):
        self.socket.close()


if __name__ == '__main__':
    client = Client01()
    client.send()
    client.recive()
    client.close()
