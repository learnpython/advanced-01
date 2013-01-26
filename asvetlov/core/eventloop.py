import itertools
import os
import select
import socket
import time

from select import EPOLLIN, EPOLLOUT, EPOLLHUP, EPOLLERR, EPOLLET


from .timeloop import Timeloop
from .proto import Transport, Protocol



class Eventloop(Timeloop):
    def __init__(self, *, check_args=True):
        super().__init__(check_args=check_args)
        self._running = True
        self._stopping = False
        self._readers = {}
        self._writers = {}
        self._poll = select.epoll()

    def close(self):
        super().close()
        self._poll.close()
        for fd in itertools.chain(self._readers, self._writers):
            try:
                os.close(fd)
            except OSError:
                pass
        self._readers = self._writers = {}

    def run_once(self, timeout):
        delay = self._process_timers()
        delay = timeout if timeout < delay else delay
        self._process_poll(delay)

    def run_iter(self, timeout):
        now = time.time()
        while time.time() - now < timeout:
            self.run_once(time.time() - now)
            if not self._soon and not self._later:
                break

    def run(self):
        while not self._stopping:
            self.run_once(None)

    def stop(self):
        self._stopping = True
        self._signal(b'Q')

    def listen(self, addr, protocol_factory, reuse_addr=True):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        if reuse_addr:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(addr)
        sock.listen(10)
        def connector(fd, event):
            if event & EPOLLERR:
                err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                if err != 0:
                    raise OSError(err, 'Connect call failed')
            if event & EPOLLHUP:
                raise OSError('Connect is hunging')
            conn, peer_addr = sock.accept()
            newfileno = conn.fileno()
            conn.setblocking(False)
            transport = Transport(self, conn, addr)
            protocol = protocol_factory()
            protocol.connection_made(transport)
            def reader(fd, event):
                try:
                    read = conn.recv(1024*1024)
                    protocol.data_received(read)
                except BlockingIOError:
                    pass
                except OSError as ex:
                    protocol.connection_lost(ex)
                else:
                    if transport.closing and not transport._writing:
                        protocol.connection_lost(None)
            def writer(fd, event):
                try:
                    transport._write(fd, event)
                except OSError as ex:
                    protocol.connection_lost(ex)
                else:
                    if transport.closing and not transport._writing:
                        protocol.connection_lost(None)
            self._readers[newfileno] = reader
            self._writers[newfileno] = writer
            events = EPOLLIN|EPOLLERR|EPOLLHUP
            self._poll.register(newfileno, events)
        fileno = sock.fileno()
        self._readers[fileno] = connector
        events = EPOLLIN|EPOLLERR|EPOLLHUP
        self._poll.register(fileno, events)

    def _process_poll(self, delay):
        try:
            events = self._poll.poll(delay)
        except InterruptedError:
            return
        for fd, event in events:
            ex = None
            if event & EPOLLHUP:
                ex = OSError('socket hanging')
            if event & EPOLLERR:
                sock = socket.fromfd(fd, socket.AF_INET, socket.SOCK_STREAM)
                err = sock.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
                sock.close()
                if err != 0:
                    ex = OSError(err, 'socket error')
            if ex:
                if fd in self._readers:
                    cb = self._readers[fd]
                elif fd in self._writers:
                    cb = self._writers[fd]
                else:
                    cb = None
                if cb:
                    self._soon.append(lambda: cb(fd, event))
            if event & EPOLLIN and fd in self._readers:
                cb = self._readers[fd]
                self._soon.append(lambda: cb(fd, event))
            if event & EPOLLOUT and fd in self._writers:
                cb = self._writers[fd]
                self._soon.append(lambda: cb(fd, event))
