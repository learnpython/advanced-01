import socket


class Server01:

    def __init__(self, host='127.0.0.1', port=6666, max_queue=1):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.listen(max_queue)

    def serve(self):
        conn, addr = self.socket.accept()
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)
        conn.close()

    def shutdown(self):
        self.socket.close()
