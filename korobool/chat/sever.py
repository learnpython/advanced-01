__author__ = 'Oleksandr Korobov'

import socket
from korobool.chat.Threaded import ServingThreadWrapper

class ChatServer:
    def __init__(self, PORT=50007):
        self.port = PORT
        self.host = ''
        self.__clients_pool = []

    def serve(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while True:
            self.socket.listen(5)
            conn, addr = self.socket.accept()
            self.start_serve_connection(conn, addr)

    def start_serve_connection(self, conn, addr):
        self.__clients_pool.append(ServingThreadWrapper(self, conn, addr))

    def notify(self, sender, message):
        print('Notification received:', message)
        for client in self.__clients_pool:
            print(client.Name)

chat_sever = ChatServer(PORT = 50007)
chat_sever.serve()