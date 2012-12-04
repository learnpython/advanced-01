# coding=utf-8


def prepare_data_for_sending(data):
    bytes = data.encode('utf-8')
    bytes_length = len(bytes)
    return bytes_length.to_bytes(2, byteorder='big') + bytes


def parse_recieved_bytes(bytes):
    parsed_list = bytes.decode('utf-8').split(' ', 1)
    return (
        parsed_list[0],
        parsed_list[1] if len(parsed_list) == 2 else None
    )
