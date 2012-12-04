__author__ = 'Oleksandr Korobov'

import socket
from korobool.chat.Threaded import ServingThreadWrapper

class ChatServer:
    def __init__(self, PORT=50007):
        self.port = PORT
        self.host = ''
        self.__clients_pool = []
        self.closing = False

    def serve(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        while not self.closing:
            self.socket.listen(5)
            conn, addr = self.socket.accept()
            self.start_serve_connection(conn, addr)
        self.close_all_clients()

    def start_serve_connection(self, conn, addr):
        stw = ServingThreadWrapper(self, conn, addr)
        self.__clients_pool.append(stw)

    def notify(self, sender, message):
        print('Notification received:', message)
        if message[0] == b'CMD_STOP':
            self.close_all_clients()
            self.socket.close()

        if message[0] == b'CMD_GONE':
            print('Not implemented yet')

        if message[0] == b'CMD_MSGE':
            print('Not implemented yet')

    def close_all_clients(self):
        for client in self.__clients_pool:
            client.close()
        self.__clients_pool.clear()

chat_sever = ChatServer(PORT = 50007)
chat_sever.serve()