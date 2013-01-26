import abc
import socket

from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR, EPOLLET


class Transport:
    def __init__(self, eventloop, sock, addr):
        self.eventloop = eventloop
        self.sock = sock
        self.fileno = sock.fileno()
        self.peer_addr = addr
        self.buffer = bytearray()
        self.closing = False
        self._writing = False

    def write(self, data):
        if self.closing or not self.sock:
            raise RuntimeError("Closed")
        self.buffer.extend(data)
        if not self._writing:
            self._writing = True
            self.eventloop._poll.modify(self.fileno,
                                        EPOLLOUT|EPOLLERR|EPOLLHUP)

    def _write(self, fd, event):
        if event & EPOLLERR:
            err = fd.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
            if err != 0:
                raise OSError(err, 'Connect call failed')
        if event & EPOLLHUP:
            raise OSError('Connect is hunging')
        try:
            sent = self.sock.send(self.buffer)
            del self.buffer[:sent]
            if not self.buffer:
                self.eventloop._poll.modify(self.fileno,
                                            EPOLLIN|EPOLLERR|EPOLLHUP)
                self._writing = False
        except BlockingIOError:
            pass

    def writelines(self, iterable):
        if self.closing or not self.fd:
            raise RuntimeError("Closed")
        for l in iterable:
            self.write(l)

    def close(self):
        self.closing = True

    def abort(self):
        self.closing = True
        self._writing = False
        self.eventloop._readers.pop(self.fileno)
        self.eventloop._writers.pop(self.fileno)
        self.sock.close()
        try:
            self.eventloop._poll.unregister(self.fileno)
        except KeyError:
            pass


class Protocol(metaclass=abc.ABCMeta):
    transport = None

    def connection_made(self, transport):
        self.transport = transport

    @abc.abstractmethod
    def data_received(self, data):
        pass

    @abc.abstractmethod
    def connection_lost(self, exc):
        if self.transport:
            self.transport.abort()
        self.transport = None
