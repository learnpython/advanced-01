__author__ = 'Oleksandr Korobov'

import threading
from collections import deque

class ServingThreadWrapper():

    __global_sync = object()

    def __init__(self, observer, conn, addr):
        self.name = 'no_name'
        self.observer = observer
        self.commands_queue = deque()
        self.__local_sync = object()
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=ServingThreadWrapper.serve, args=(self,))
        self.closing = False
        self.thread.start()

    def send(self, data):
        with threading.Lock(self.__local_sync):
            self.commands_queue.appendleft(data)

    def post(self, data):
        with threading.Lock(self.__local_sync):
            self.commands_queue.append(data)

    def pop_command(self):
        with threading.Lock(self.__local_sync):
            if self.commands_queue.count() > 0:
                return self.commands_queue.pop()

    # Thread-safe notifier to observer
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

            ServingThreadWrapper.process_server_messages(stw)
            # Implement communication protocol here
            data = stw.conn.recv(128)
            if not data: break
            command = repr(data)

            if command == b'CMD_STOP':
                stw.notify(('CMD_STOP',))
                break

            if command == b'CMD_GONE':
                #stw.notify(())
                break

            if command == b'CMD_MSGE':
                #stw.notify(())
                break

            if command == b'CMD_PING':
                stw.conn.sendall(b'MSG_PONG')
                break

            print('unsupported operation', command)

    @staticmethod
    def process_server_messages(stw):
        command = stw.pop_command()
        if command is None:
            return
        if command == 'MSG_SCL':
            stw.conn.sendall(b'MSG_SCL')
