__author__ = 'Oleksandr Korobov'

import socket
import json
import struct

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def receive_and_parse_command():

    header = s.recv(4)
    if not header: return

    size = int(struct.unpack('i', header)[0])
    print('receiving bytes:', size)

    body = s.recv(size).decode('utf-8')

    #print('!DATA!\n', body)

    command = json.loads(body)

    return command

while True:
    command_text = input("Enter command: ")

    package = None

    if command_text.upper() == 'PING':
        package = {'cmd': 'CMD_PING'}

    data = json.dumps(package)

    b = bytes(data, 'utf-8')
    s.sendall(struct.pack('i', len(data)))

    s.sendall(b)

    #print('sent data...' , b.decode('utf-8'))
    #s.sendall(b)
    print(receive_and_parse_command())

#s.close()
