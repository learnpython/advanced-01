#!/usr/bin/env python
# -*- coding:utf-8 -*-
import signal
import socket
import sys


def sig_handler(signum, frame):
    global client
    if client and getattr(client, 'connected'):
        client.connected = False


class Client:
    connected = False
    CHUNK_SIZE = 1024

    def __init__(self, host='localhost', port=39999):
        self.host = host
        self.port = int(port)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((self.host, self.port))
        except socket.error as e:
            print("Can't connect to server: %s, %s" % (e.errno, e.strerror))
            sys.exit(2)
        else:
            self.connected = True

    def start(self):
        while self.connected:
            input_data = input('=> ')
            if len(input_data.strip()):
                self.send(input_data)
                data = self.recv()
                print(data)
        self.socket.close()

    def send(self, data):
        snd_data = data.encode('utf-8')
        self.socket.sendall(snd_data)

    def recv(self):
        rcv_data = self.socket.recv(self.CHUNK_SIZE)
        data = rcv_data.decode('utf-8')
        return data


if __name__ == '__main__':
    client = Client()
    signal.signal(signal.SIGINT, sig_handler)

    client.start()
    sys.exit(0)
