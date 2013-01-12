import select
import socket


from timerloop import Timeloop
from proto import Transport, Protocol



class Eventloop(Timeloop):
    def __init__(self, *, check_args=True):
        super().__init__(check_args=check_args)
        self._running = True
        self._stopping = False
        self._readers = {}
        self._writers = {}
        self._connectors = {}
        self._pool = select.epoll()

    def run_once(self, timeout):
        pass

    def run(self):
        pass

    def stop(self):
        self._stopiing = True
        self._signal(b'Q')

    def connect(self, addr, protocol):
        pass

    def listen(self, addr, protocol):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(addr)
        def connector(fd, event):
            assert fd is sock
            conn, peer_addr = sock.accept()
            transport = Transport(self, conn, addr)
            protocol.connection_made(transport)
            self._readers[conn]
        def reader(fd, event):
            pass
        def writer(fd, event):
            pass
        self._connectors[sock] = connector
        events = select.EPOLLIN|select.EPOLLERR|select.EPOLLHUP
        self._pool.register(sock, events)
