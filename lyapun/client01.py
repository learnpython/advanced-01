# coding=utf-8

import socket

from work.cmdargs import parse_arguments
from work.general import recieve_data_from_socket
from work.utils import prepare_data_for_sending, parse_recieved_bytes


if __name__ == "__main__":
    args = parse_arguments()
    HOST = args.host
    PORT = args.port

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.0)
    sock.connect((HOST, PORT))

    sock.sendall(prepare_data_for_sending('connect'))
    data = sock.recv(1024)
    print ('<<< ', data)

    while True:
        user_input = input('>>> ')
        sock.sendall(prepare_data_for_sending(user_input))
        data = recieve_data_from_socket(sock)
        print ('<<< ', data)
        command, _ = parse_recieved_bytes(data)
        if command in ['ackquit', 'ackfinish']:
            break

    sock.close()
