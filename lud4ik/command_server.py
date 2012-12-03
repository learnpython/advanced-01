import os
import socket
import signal
import threading

from work.utils import format_reply


class ServerFinishException(Exception):
    pass


def shutdown_handler(signum, frame):    
    raise ServerFinishException()

signal.signal(signal.SIGUSR1, shutdown_handler)


class CommandServer:

    MAX_CONN = 5
    clients = []
    threads = {}
    commands = ['ping', 'pingd', 'quit', 'finish']
    single_reply_commands = ['ping', 'pingd']

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(100.0)
        self.socket.bind((host, port))

    def run(self):
        while True:
            self.socket.listen(self.MAX_CONN)
            conn, addr = self.socket.accept()
            self.clients.append(conn)
            print('client connected')
            th = threading.Thread(target=self.run_client, args=(conn, addr))
            self.threads[addr] = th
            th.start()

    def run_client(self, conn, addr):        
        while True:
            msg = bytes()            
            msg_len = int(conn.recv(4))
            while len(msg) < msg_len:
                try:
                    chunk = conn.recv(msg_len - len(msg))
                except socket.timeout:
                    conn.close()
                    del self.threads[addr]
                    raise SystemExit()                
                msg += chunk

            msg = msg.decode('utf-8').split('\n')            
            command_name = msg[0]
            command = getattr(self, command_name)
            if command_name == 'quit':
                args = [conn, addr]
            elif command_name in self.single_reply_commands:
                args = [conn]
            else:
                args = [addr]
            if len(msg) > 1:
                args.append(msg[1])
            command(*args)

    def connect(self, addr):
        reply = format_reply("{}\n{}".format('connected', addr))
        for conn in self.clients:
            conn.sendall(reply)

    def ping(self, conn):
        reply = format_reply('pong')
        conn.sendall(reply)

    def pingd(self, conn, data):
        reply = format_reply('{}\n{}'.format('pongd', data))
        conn.sendall(reply)

    def quit(self, conn, addr):
        reply = format_reply("{}\n{} disconnected.".format('ackquit', addr))
        for client in self.clients:
            client.sendall(reply)
        conn.close()
        del self.threads[addr]
        raise SystemExit()

    def finish(self, addr):
        reply = format_reply("{}\n{} finished server.".format('ackfinish', addr))
        for conn in self.clients:
            conn.sendall(reply)       
        os.kill(os.getpid(), signal.SIGUSR1)

    def shutdown(self):
        self.socket.close()
        print('socket closed')
        for conn in self.clients:
            conn.close()
        print('connections closed')
        for th in self.threads.values():
            th.join()
        print('threads closed')
        raise SystemExit()


if __name__ == '__main__':
    server = CommandServer('', 50007)
    try:
        server.run()
    except ServerFinishException:
        server.shutdown()
        







