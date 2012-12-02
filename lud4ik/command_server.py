import os
import socket
import signal
import threading


class ServerFinishException(Exception):
    pass


def shutdown_handler(signum, frame):    
    raise ServerFinishException()

# check signal
signal.signal(signal.SIGINT, shutdown_handler)


class CommandServer:

    MAX_CONN = 5
    clients = []
    threads = {}
    single_reply_commands = ['ping', 'pingd']    

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(1.0)
        self.socket.bind((host, port))        

    def run(self):
        while True:
            self.socket.listen(self.MAX_CONN)
            conn, addr = self.socket.accept()
            self.clients.append(conn)
            th = threading.Thread(target=self.run_client, args=(conn, addr))
            threads[addr] = th
            th.start()

    def run_client(self, conn, addr):
        while True:
            msg = ''
            msg_len = int(self.socket.recv(4))

            while len(msg) < msg_len:
                try:
                    chunk = conn.recv(msg_len - len(msg))
                except socket.timeout:
                    conn.close()
                    del self.threads[addr]
                    raise SystemExit()                                    
                msg += chunk

            msg = msg.split('\n')
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
        reply = self.format_reply("{}\n{}".format('connected', addr))        
        for conn in self.clients:
            conn.sendall(reply)

    def ping(self, conn):
        reply = self.format_reply('pong')
        conn.sendall(reply)        

    def pingd(self, conn, data):
        reply = self.format_reply('{}\n{}'.format('pongd', data))
        conn.sendall(reply) 

    def quit(self, conn, addr):
        reply = self.format_reply("{}\n{} disconnected.".format('ackquit', addr))
        for client in self.clients:
            client.sendall(reply)
        conn.close()
        del self.threads[addr]
        raise SystemExit()

    def finish(self, addr):
        reply = self.format_reply("{}\n{} finished server.".format('ackfinish', addr))
        for conn in self.clients:
            conn.sendall(reply)
        # need appropriate params
        os.kill()      

    def format_reply(self, text):
        return "{:4}{}".format(len(reply), reply)

    def shutdown(self):
        self.socket.close()
        for conn in self.clients:
            conn.close()
        for th in self.threads:
            th.join()
        raise SystemExit()


if __name__ == '__main__':
    server = CommandServer('', 50007)
    try:
        server.run()
    except ServerFinishException:
        server.shutdown()







