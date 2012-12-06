from contextlib import closing
import os
import threading
import sys

__author__ = 'Oleksandr Korobov'

import socket
import json
import struct

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))


def close_client():
    pid = os.getpid()
    os.kill(pid, 9)


def receive_and_parse_command():

    while True:
        try:
            header = s.recv(4)
            if not header: break
        except:
            print('connection error. exiting...')
            close_client()


        size = int(struct.unpack('i', header)[0])
        print('receiving bytes:', size)

        body = s.recv(size).decode('utf-8')
        command = json.loads(body)

        print('data from server', command)

        if command['cmd'] == 'CMD_CLOSE':
            close_client()


read_thread = threading.Thread(target=receive_and_parse_command)
read_thread.start()

print("Enter commands: ")

while True:
    command_text = input()

    package = None

    if command_text.upper() == 'PING':
        package = {'cmd': 'CMD_PING'}

    if command_text.upper() == 'BROADCAST':
        message = input("Enter broadcast message: ")
        package = {'cmd': 'CMD_BROADCAST', 'msg': message}

    if command_text.upper() == 'MESSAGE':
        print('Not supported by server yet')
        user_id = input("Enter user id: ")
        message = input("Enter message: ")
        package = {'cmd': 'CMD_MESSAGE', 'msg': message}

    if command_text.upper() == 'SCLOSESERVER':
        package = {'cmd': 'CMD_SCLOSESERVER'}

    data = json.dumps(package)

    b = bytes(data, 'utf-8')
    s.sendall(struct.pack('i', len(data)))

    s.sendall(b)


#read_thread.join()
#s.close()
