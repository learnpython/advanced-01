__author__ = 'Oleksandr Korobov'

import threading

class ServingThreadWrapper():

    __global_sync = object()

    def __init__(self, observer, conn, addr):
        self.name = 'no_name'
        self.observer = observer
        self.conn = conn
        self.addr = addr
        self.thread = threading.Thread(target=ServingThreadWrapper.serve, args=(self,))
        self.closing = False
        self.thread.start()

    # Thread-safe notifier to observer
    def notify(self, message):
        with threading.RLock(ServingThreadWrapper.__global_sync):
            self.observer.notify(self, message)

    def close(self):
        self.closing = True
        self.thread.join()

    # This method is executed in separate thread. Be aware of synchronization issues.
    # All updates globally accessible variables or calls to thread-unsafe methods/functions
    # must be done in synchronization block.
    @staticmethod
    def serve(stw):
        print('Connection attempt', stw.addr)
        while not stw.closing:
            # Implement communication protocol here
            data = stw.conn.recv(128)
            if not data: break
            command = repr(data)

            if command == b'CMD_STOP':
                #stw.notify(())
                pass

            if command == b'CMD_GONE':
                #stw.notify(())
                pass

            if command == b'CMD_MSGE':
                #stw.notify(())
                pass