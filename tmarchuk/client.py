#!/usr/bin/env python
# -*- coding:utf-8 -*-
import signal
import socket
import sys
import threading


def sig_handler(signum, frame):
    global client
    if client and getattr(client, 'stop'):
        client.stop.set()


class Client:
    cmd_list = ['connected', 'pong', 'pongd', 'ackreply', 'ackfinish']

    def __init__(self, host='localhost', port=39999):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except socket.error as e:
            print("Can't connect to server: {}, {}".format(e.errno, e.strerror))
            sys.exit(2)
        self.stop = threading.Event()

    def start(self):
        self.rcv_thread = threading.Thread(target=self.rcv_handler)
        self.rcv_thread.start()
        while not self.stop.wait(0):
            input_data = input('=> ')
            if len(input_data.strip()):
                data = '\n'.join(input_data.split(' ', 1))
                self.send(data)
        self.terminate()

    def terminate(self):
        self.socket.close()
        self.rcv_thread.join()

    def parse_data(self, data):
        data_list = data.split('\n', 1)
        return data_list[0], data_list[1:]

    def rcv_handler(self):
        while not self.stop.wait(0):
            data = self.recv()
            if not data:
                print("Connection closed by server")
                self.stop.set()
                break
            cmd, cmd_args = self.parse_data(data)
            if cmd in self.cmd_list and callable(getattr(self, cmd, None)):
                getattr(self, cmd)(cmd_args)
            else:
                print(data)

    def connected(self, data):
        print('New client connected from {}'.format(data))

    def ackquit(self, data):
        print('Someone has gone: "{}"'.format(data))

    def ackfinish(self, data):
        print("Server is going down!")
        self.terminate()

    def send(self, data):
        snd_data = data.encode('utf-8')
        snd_length = int(len(snd_data)).to_bytes(4, 'big')
        self.socket.sendall(snd_length)
        self.socket.sendall(snd_data)

    def recv(self):
        rcv_length = int.from_bytes(self.socket.recv(4), 'big')
        rcv_data = self.socket.recv(rcv_length)
        data = rcv_data.decode('utf-8')
        return data

if __name__ == '__main__':
    client = Client()
    signal.signal(signal.SIGINT, sig_handler)

    client.start()
    sys.exit(0)
