# coding=utf-8


def recieve_data_from_socket(connection):
    data_length_bytes = connection.recv(2)
    data_length = int.from_bytes(data_length_bytes, byteorder='big')
    data = connection.recv(data_length)
    return data
