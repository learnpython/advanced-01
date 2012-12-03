import socket
import threading

from work.utils import format_reply


class CommandClient:

    reply_commands = ['connected', 'pong', 'pongd', 'ackquit', 'ackfinish']
    print_reply_commands = ['connected', 'pong', 'pongd']

    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET,
                                    socket.SOCK_STREAM)
        self.socket.settimeout(1.0)
        self.socket.connect((host, port))

    def run(self):
        self.thread = threading.Thread(target=self.recv_response)
        self.thread.start()
        while True:
            command = input()            
            if command in ['q', 'quit']:
                break
            command_name = command.split()[0]
            command = command.replace(' ', '\n')            
            self.socket.sendall(format_reply(command))
            if command_name == 'quit':
                self.quit()                
        self.socket.close()

    def recv_response(self):
        while True:
            msg = self.get_reply()
            command_name = msg.split('\n')[0]
            if command_name in self.print_reply_commands:
                print(msg)
            elif command_name in ['ackquit', 'ackfinish']:
                self.close()

    def get_reply(self):
        msg = bytes()
        msg_len = int(self.socket.recv(4))
        while len(msg) < msg_len:
            try:
                chunk = self.socket.recv(msg_len - len(msg))
            except socket.timeout:
                # can be in thread or main; correctly disconnect
                self.socket.close()               
                raise SystemExit()                
            msg += chunk

        msg = msg.decode('utf-8')
        return msg

    def quit(self):
        reply = self.get_reply()
        if reply.find('ackquit')!= -1:
            self.close()

    def close(self):
        self.socket.close()             
        raise SystemExit()


if __name__ == '__main__':
    client = CommandClient('', 50007)
    client.run()
