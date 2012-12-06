import sys

__author__ = 'Oleksandr Korobov'

import socket
import signal

from korobool.chat.Threaded import ServingThreadWrapper

class ChatServer:
    def __init__(self, PORT=50007):
        self.port = PORT
        self.host = ''
        self.__clients_pool = []
        self.closing = False

    def __start_serve_connection(self, conn, addr):
        stw = ServingThreadWrapper(self, conn, addr)
        self.__clients_pool.append(stw)

    def __close_all_clients(self):
        for client in self.__clients_pool:
            client.close()
        self.__clients_pool.clear()

    def serve(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))

        while not self.closing:
            self.socket.listen(5)
            conn, addr = self.socket.accept()
            self.__start_serve_connection(conn, addr)
        self.__close_all_clients()

    def stop_serve(self):
        self.closing = True
        print('Proper server closing  is not implemented yet...')

    def notify(self, sender, message):
        print('Notification received:', message)
        if message['cmd'] == 'CMD_BROADCAST':
            for client in self.__clients_pool:
                if not client is None and not client.closing:
                    #print('Posting to '. client.name)
                    client.post(message)
        if message['cmd'] == 'CMD_MESSAGE':
            client.post({'cmd': 'CMD_SEVER_WARNING', 'msg': 'message sending is not implemented yet'})


chat_sever = ChatServer(PORT = 50007)

def signal_handler(signal, frame):
    print('CTRL+C caught. Wait... Server is closing now....')
    chat_sever.stop_serve()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

chat_sever.serve()