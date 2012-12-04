__author__ = 'Oleksandr Korobov'

import socket

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.sendall(b'Hello, world')
#while True:
data = s.recv(1024)
print('Received', repr(data))

s.close()
