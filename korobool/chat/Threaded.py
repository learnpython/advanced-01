__author__ = 'Oleksandr Korobov'

import threading
from collections import deque
import json
import struct

class ServingThreadWrapper():

    __global_sync = threading.RLock()        # Synchronization with main and all client threads

    def __init__(self, observer, conn, addr):
        self.name = 'no_name'
        self.observer = observer
        self.commands_queue = deque()       # each client has independent commands queue
        self.__local_sync = threading.Lock()       # synchronization between main and client thread
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=ServingThreadWrapper.__serve, args=(self,))
        self.closing = False
        self.thread.start()

    # Thread safe first priority message
    def send(self, data):
        with self.__local_sync:
            self.commands_queue.appendleft(data)

    # Thread safe first idle message
    def post(self, data):
        with self.__local_sync:
            self.commands_queue.append(data)

    # Thread safe pop command operation
    def pop_command(self):
        with self.__local_sync:
            if len(self.commands_queue) > 0:
                return self.commands_queue.pop()

    # Thread-safe sever notifier
    def notify(self, message):
        with ServingThreadWrapper.__global_sync:
            self.observer.notify(self, message)

    def close(self):
        # Send closing message to client and then close the connection
        print('Closing notification to client is not implemented yet...')
        self.closing = True
        self.thread.join()

    # These methods ere executed in separate thread. Be aware of synchronization issues.
    # All updates globally accessible variables or calls to thread-unsafe methods/functions
    # must be done in synchronization block.
    @staticmethod
    def __serve(stw):
        print('Connection attempt', stw.addr)
        while not stw.closing:
            ServingThreadWrapper.__process_server_messages_queue(stw) # It might be good idea to move this to new thread
            command = ServingThreadWrapper.__receive_and_parse_client_command(stw)
            ServingThreadWrapper.__process_command(stw, command)

    @staticmethod
    def __process_server_messages_queue(stw):
        package = stw.pop_command()
        if package is None:
            return

        data = json.dumps(package)

        b = bytes(data, 'utf-8')
        stw.conn.sendall(struct.pack('i', len(data)))

        stw.conn.sendall(b)
        print('sent data...' , b.decode('utf-8'))

    @staticmethod
    def __receive_and_parse_client_command(stw):

        header = stw.conn.recv(4)
        if not header: return

        size = int(struct.unpack('i', header)[0])
        print('receiving bytes:', size)

        body = stw.conn.recv(size).decode('utf-8')

        if not body:
            print('Protocol error. Closing client connection.')
            stw.closing = True

        print('!DATA!\n', body)

        command = json.loads(body)

        if not command:
            print('Protocol error. Closing client connection.')
            stw.closing = True

        return command

    @staticmethod
    def __process_command(stw, command):
        print('new command from client received', command['cmd'])
        if command['cmd'] == 'CMD_PING':
            stw.send({'cmd': 'CMD_PONG', 'msg': 'pong from server'})
