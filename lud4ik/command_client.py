import os
import signal
import socket
import threading

from work.utils import format_reply
from work.cmdargs import get_cmd_args
from work.exceptions import ClientFinishException


def shutdown_handler(signum, frame):
    raise ClientFinishException()


class CommandClient:

    session_id = None
    TIMEOUT = 10.0
    reply_commands = ['connected', 'pong', 'pongd', 'ackquit', 'ackfinish']
    print_reply_commands = ['pong', 'pongd']

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.settimeout(self.TIMEOUT)
        self.socket.connect((host, port))

    @classmethod
    def run_client(cls, host, port):
        client = cls(host, port)
        try:
            client.run()
            signal.signal(signal.SIGUSR1, shutdown_handler)
        except ClientFinishException:
            client.shutdown()
        finally:
            pass

    def run(self):
        self.thread = threading.Thread(target=self.recv_response)
        self.thread.start()
        while True:
            command = input()
            command_name = command.split()[0]
            command = command.replace(' ', '\n')
            self.socket.sendall(format_reply(command))

    def recv_response(self):
        while True:
            msg = self.get_reply()
            parts = msg.split('\n')
            command_name = parts[0]
            if command_name in self.print_reply_commands:
                print(msg)
            elif command_name == 'connected':
                if parts[-1].startswith('session'):
                    self.session_id = parts[-1][7:]
                print(msg)
            elif command_name == 'ackquit':
                if parts[-1] == self.session_id:
                    self.close()
                else:
                    print(msg)
            elif command_name == 'ackfinish':
                self.close()

    def get_reply(self):
        msg = bytes()
        msg_len = int(self.socket.recv(4))
        while len(msg) < msg_len:
            try:
                chunk = self.socket.recv(msg_len - len(msg))
            except socket.timeout:
                self.close()
            msg += chunk
        msg = msg.decode('utf-8')
        return msg

    def close(self):
        os.kill(os.getpid(), signal.SIGUSR1)

    def shutdown(self):
        self.socket.close()
        print('socket closed')
        self.thread.join()
        print('thread closed')
        raise SystemExit()


if __name__ == '__main__':
    args = get_cmd_args()
    CommandClient.run_client(args.host, args.port)