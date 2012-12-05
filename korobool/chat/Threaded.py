__author__ = 'Oleksandr Korobov'

import threading
from collections import deque
import json

class ServingThreadWrapper():

    __global_sync = object()        # Synchronization with main and all client threads

    def __init__(self, observer, conn, addr):
        self.name = 'no_name'
        self.observer = observer
        self.commands_queue = deque()       # each client has independent commands queue
        self.__local_sync = object()        # synchronization between main and client thread
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=ServingThreadWrapper.serve, args=(self,))
        self.closing = False
        self.thread.start()

    # Thread safe first priority message
    def send(self, data):
        with threading.Lock(self.__local_sync):
            self.commands_queue.appendleft(data)

    # Thread safe first idle message
    def post(self, data):
        with threading.Lock(self.__local_sync):
            self.commands_queue.append(data)

    # Thread safe pop command operation
    def pop_command(self):
        with threading.Lock(self.__local_sync):
            if self.commands_queue.count() > 0:
                return self.commands_queue.pop()

    # Thread-safe sever notifier
    def notify(self, message):
        with threading.RLock(ServingThreadWrapper.__global_sync):
            self.observer.notify(self, message)

    def close(self):
        self.send('MSG_SCL')
        self.closing = True
        self.thread.join()

    # These methods ere executed in separate thread. Be aware of synchronization issues.
    # All updates globally accessible variables or calls to thread-unsafe methods/functions
    # must be done in synchronization block.
    @staticmethod
    def serve(stw):
        print('Connection attempt', stw.addr)
        while not stw.closing:

            ServingThreadWrapper.__process_server_messages_queue(stw)

            message = ServingThreadWrapper.__get_and_parse_client_message(stw)

            command = json.loads(repr(message))

            if command['cmd'] == b'CMD_STOP':
                stw.notify(('CMD_STOP',))
                break

            if command['cmd'] == b'CMD_GONE':
                #stw.notify(())
                break

            if command['cmd'] == b'CMD_MSGE':
                #stw.notify(())
                break

            if command['cmd'] == b'CMD_PING':
                stw.conn.sendall(b'MSG_PONG')
                break

            print('unsupported operation', command, 'closing client connection')
            stw.closing = True

    @staticmethod
    def __process_server_messages_queue(stw):
        command = stw.pop_command()
        if command is None:
            return

        if command[0] == 'MSG_SCL':
            stw.conn.sendall(b'MSG_SCL')

        if command[0] == 'MSG_MSG':
            stw.conn.sendall(command[1])

    @staticmethod
    def __get_and_parse_client_message(stw):

        header = stw.conn.recv(8)
        if not header: return

        # Validate header
        def is_valid_header(header):
            return True

        if not is_valid_header(header):
            stw.closing = True
            return


