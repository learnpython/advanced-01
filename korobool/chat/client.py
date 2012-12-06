__author__ = 'Oleksandr Korobov'

import socket
import json
import struct

HOST = 'localhost'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

package = {
    'cmd': 'CMD_CONNECT',
    'name': 'ClientXXX'}

data = json.dumps(package)



#s_data = struct.pack('b', data)

b = bytes(data, 'utf-8')
s.sendall(struct.pack('i', len(data)))

s.sendall(b)

print('sent data...' , b.decode('utf-8'))
#s.sendall(b)

#while True:
data = s.recv(1024)
print('Received', repr(data))

s.close()
