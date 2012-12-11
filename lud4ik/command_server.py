import os
import os.path
import socket
import signal
import logging
import threading
from operator import attrgetter
from collections import namedtuple

from work.protocol import Feeder
from work.models import cmd
from work.cmdargs import get_cmd_args
from work.exceptions import ServerFinishException
from work.utils import (format_reply,
                        get_random_hash,
                        handle_timeout,
                        get_msg,
                        configure_logging,
                        get_keyword_args)


def shutdown_handler(signum, frame):
    raise ServerFinishException()


class CommandServer:

    MAX_CONN = 5
    TIMEOUT = 1.0
    CHUNK_SIZE = 1024
    PID_FILE = 'server.pid'
    clients = {}
    commands = [cmd.CONNECT, cmd.PING, cmd.PINGD, cmd.QUIT, cmd.FINISH]
    templ = namedtuple('templ', 'addr, thread, session')

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.settimeout(self.TIMEOUT)
        self.socket.bind((host, port))

    @classmethod
    def run_server(cls, host, port):
        server = cls(host, port)
        try:
            handler = signal.signal(signal.SIGINT, shutdown_handler)
            with open(cls.PID_FILE, 'w') as f:
                f.write(str(os.getpid()))
            server.run()
        except (ServerFinishException, OSError):
            server.shutdown()
        finally:
            signal.signal(signal.SIGINT, handler)

    def run(self):
        self.socket.listen(self.MAX_CONN)
        while True:
            with handle_timeout():
                conn, addr = self.socket.accept()
                th = threading.Thread(target=self.run_client, args=(conn, ))
                self.clients[conn] = self.templ(addr=addr,
                                                thread=th,
                                                session=get_random_hash())
                th.start()

    def run_client(self, conn):
        feeder = Feeder(self.commands)
        tail = bytes()
        while True:
            try:
                chunk = tail + conn.recv(self.CHUNK_SIZE)
                packet, tail = feeder(chunk)
                if not packet:
                    continue
                process = getattr(self, packet.__class__.__name__.lower())
                kwargs = {'packet': packet}
                kw_only = get_keyword_args(process)
                if 'conn' in kw_only:
                    kwargs['conn'] = conn
                process(packet, **kwargs)
            except (socket.timeout, OSError):
                conn.close()
                self.clients.pop(conn, None)
                return

    def connect(self, packet, *, conn):
        session = self.clients[conn].session
        reply = packet.reply(session)
        for client in list(self.clients.keys()):
            conn.sendall(reply)

    def ping(self, packet, *, conn):
        reply = packet.reply()
        conn.sendall(reply)

    def pingd(self, packet, *, conn):
        reply = packet.reply()
        conn.sendall(reply)

    def quit(self, packet, *, conn):
        session = self.clients[conn].session
        reply = packet.reply(session)
        for client in list(self.clients.keys()):
            conn.sendall(reply)
        conn.close()
        self.clients.pop(conn, None)
        raise SystemExit()

    def finish(self, packet):
        reply = packet.reply()
        for client in list(self.clients.keys()):
            client.sendall(reply)
        os.kill(os.getpid(), signal.SIGINT)
        raise SystemExit()

    def shutdown(self):
        self.socket.close()
        logging.info('socket closed')
        for conn in list(self.clients.keys()):
            conn.close()
        logging.info('connections closed')
        for th in map(attrgetter('thread'), list(self.clients.values())):
            th.join()
        logging.info('threads closed')
        if os.path.exists(self.PID_FILE):
            os.remove(self.PID_FILE)
        raise SystemExit()


if __name__ == '__main__':
    configure_logging('Server')
    args = get_cmd_args()
    CommandServer.run_server(args.host, args.port)