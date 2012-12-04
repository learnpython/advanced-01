__author__ = 'Oleksandr Korobov'

import threading

class ServingThreadWrapper():

    __global_sync = object()

    def __init__(self, observer, conn, addr):
        self.name = 'noname'
        self.observer = observer
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=ServingThreadWrapper.serve, args=(self,))
        self.closing = False
        self.thread.start()

    # Thread-safe notifier to observer
    def notify(self, message):
        l = threading.RLock(ServingThreadWrapper.__global_sync)
        with l:
            self.observer.notify(self, message)

    # This method is executed in separate thread.
    # Be aware of synchronization issues.
    # All updates globally accessible variables or
    # calls to thread-unsafe methods must be done
    # in synchronization block.
    @staticmethod
    def serve(stw):
        print('Connection attempt', stw.observer, stw.conn, stw.addr)
        while not stw.closing:

            # Implement communication protocol here

            # Minimalistic test protocol
            data = stw.conn.recv(1024)
            print('Waiting for data', stw.conn, stw.addr)
            if not data: break
            stw.notify(repr(data))