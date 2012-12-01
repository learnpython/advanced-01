# coding=utf-8

import socket


HOST = ''
PORT = 50007

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((HOST, PORT))
sock.listen(1)

conn, addr = sock.accept()

print ('Connected by', addr)

while True:
    data = conn.recv(1024)
    if not data:
        break
    conn.sendall(data)

conn.close()
