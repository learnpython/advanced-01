import os
import signal
import socket
import logging

from work.protocol import Feeder, Packet
from work.models import cmd
from work.utils import configure_logging
from work.cmdargs import get_cmd_args
from work.exceptions import ClientFinishException


def shutdown_handler(signum, frame):
    raise ClientFinishException()


class CommandClient:

    session_id = None
    TIMEOUT = 1.0
    CHUNK_SIZE = 1024
    commands = [cmd.CONNECTED, cmd.PONG, cmd.PONGD, cmd.ACKQUIT, cmd.ACKFINISH]

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.settimeout(self.TIMEOUT)
        self.socket.connect((host, port))

    @classmethod
    def run_client(cls, host, port):
        client = cls(host, port)
        try:
            handler = signal.signal(signal.SIGINT, shutdown_handler)
            client.run()
        except (OSError, socket.timeout, ClientFinishException):
            client.shutdown()
        finally:
            signal.signal(signal.SIGINT, handler)

    def run(self):
        self.feeder = Feeder(self.commands)
        while True:
            command = input().split()
            kwargs = {}
            cmd_input = getattr(cmd, command[0].upper())
            if cmd_input == cmd.PINGD:
                kwargs['data'] = command[1]
            packet = eval('{}(**kwargs).pack()'.format(command[0]))
            self.socket.sendall(packet)
            self.recv_response()

    def recv_response(self):
        tail = bytes()
        while True:
            chunk = tail + self.socket.recv(self.CHUNK_SIZE)
            packet, tail = self.feeder.feed(chunk)
            if not packet:
                continue
            else:
                getattr(self, packet.__class__.__name__.lower())(packet)
                break

    def connected(self, packet):
        self.session = packet.session
        print('{} {}'.format(packet.cmd, packet.session))

    def pong(self, packet):
        print(packet.cmd)

    def pongd(self, packet):
        print('{} {}'.format(packet.cmd, packet.data))

    def ackquit(self, packet):
        print('{} {}'.format(packet.cmd, packet.session))
        self.shutdown()

    def ackfinish(self, packet):
        print(packet.cmd)
        self.shutdown()

    def shutdown(self):
        self.socket.close()
        logging.info('socket closed')
        raise SystemExit()


if __name__ == '__main__':
    configure_logging('Client')
    args = get_cmd_args()
    CommandClient.run_client(args.host, args.port)