import os
import socket
import signal
import threading
from operator import attrgetter
from collections import namedtuple

from work.cmdargs import get_cmd_args
from work.exceptions import ServerFinishException
from work.utils import format_reply, get_random_hash


def shutdown_handler(signum, frame):
    raise ServerFinishException()

signal.signal(signal.SIGUSR1, shutdown_handler)


class CommandServer:

    MAX_CONN = 5
    TIMEOUT = 100.0
    clients = {}
    commands = ['connect', 'ping', 'pingd', 'quit', 'finish']
    single_reply_commands = ['ping', 'pingd']
    templ = namedtuple('templ', 'addr, thread, session')

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(self.TIMEOUT)
        self.socket.bind((host, port))

    def run(self):
        while True:
            self.socket.listen(self.MAX_CONN)
            conn, addr = self.socket.accept()
            th = threading.Thread(target=self.run_client, args=(conn, ))
            self.clients[conn] = self.templ(addr=addr, thread=th,
                                            session=get_random_hash())
            th.start()

    def run_client(self, conn):
        while True:
            msg = bytes()
            msg_len = int(conn.recv(4))
            while len(msg) < msg_len:
                try:
                    chunk = conn.recv(msg_len - len(msg))
                except socket.timeout:
                    conn.close()
                    del self.clients[conn]
                    raise SystemExit()
                msg += chunk

            msg = msg.decode('utf-8').split('\n')
            command_name = msg[0]
            command = getattr(self, command_name)
            args = [conn]            
            if len(msg) > 1:
                args.append(msg[1])
            command(*args)

    def connect(self, conn):
        self.condition_reply(conn, "connected", reply_templ="{}\nsession{}")

    def ping(self, conn):
        reply = format_reply('pong')
        conn.sendall(reply)

    def pingd(self, conn, data):
        reply = format_reply('{}\n{}'.format('pongd', data))
        conn.sendall(reply)

    def quit(self, conn):
        self.condition_reply(conn, "ackquit", shared_templ="{}\n{} disconnected.")
        conn.close()
        del self.clients[conn]
        raise SystemExit()

    def condition_reply(self, conn, reply_command, shared_templ="{}\n{}", reply_templ="{}\n{}"):
        addr = self.clients[conn].addr
        shared_reply = format_reply(shared_templ.format(reply_command, addr))
        session_id = self.clients[conn].session
        reply = format_reply(reply_templ.format(reply_command, session_id))
        for client in self.clients.keys():
            if client == conn:
                conn.sendall(reply)
            else:
                conn.sendall(shared_reply)

    def finish(self, conn):
        addr = self.clients[conn].addr
        reply = format_reply("{}\n{} finished server.".format('ackfinish', addr))
        for client in self.clients.keys():
            client.sendall(reply)
        os.kill(os.getpid(), signal.SIGUSR1)

    def shutdown(self):
        self.socket.close()
        print('socket closed')
        for conn in self.clients.keys():
            conn.close()
        print('connections closed')
        for th in map(attrgetter('thread'), self.clients.values()):
            th.join()
        print('threads closed')
        raise SystemExit()


def run_server(host, port):
    server = CommandServer(host, port)
    try:
        server.run()
    except ServerFinishException:
        server.shutdown()


if __name__ == '__main__':
    args = get_cmd_args()
    run_server(args.host, args.port)