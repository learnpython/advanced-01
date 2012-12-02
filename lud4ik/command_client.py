import socket


class CommandClient:

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.settimeout(1.0)
        self.socket.connect((host, port))

    def run(self):
        while True:
            command = input()
            if command in ['q', 'quit']:
                break
            command = command.replace(' ', '\n')
            self.socket.sendall(command)
        self.socket.close()


if __name__ == '__main__':
    client = CommandClient('', 50007)
    client.run()
