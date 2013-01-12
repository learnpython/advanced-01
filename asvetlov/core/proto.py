import abc


class Transport:
    def __init__(self, eventloop, fd, addr):
        self.eventloop = eventloop
        self.fd = fd
        self.peer_addr = addr
        self.buffer = bytearray()
        self.closing = False

    def write(self, data):
        if self.closing or not self.fd:
            raise RuntimeError("Closed")
        self.buffer.extend(data)

    def writelines(self, iterable):
        if self.closing or not self.fd:
            raise RuntimeError("Closed")
        for l in iterable:
            self.write(l)

    def close(self):
        self.closing = True

    def abort(self):
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
        self.transport = None
