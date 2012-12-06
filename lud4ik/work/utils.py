import socket
import random
import hashlib
from contextlib import contextmanager


def format_reply(reply):
    byte_reply = bytes(reply, 'utf-8')
    return bytes("{:4}".format(len(byte_reply)), 'utf-8') + byte_reply


def get_random_hash(n=10):
    _str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_name = ''.join([random.choice(_str) for i in range(n)])
    return hashlib.sha224(random_name.encode('utf-8')).hexdigest()


@contextmanager
def handle_timeout():
    try:
        yield
    except socket.timeout:
        pass


def get_conn_data(conn, length):
    msg = bytes()
    while len(msg) < length:
        chunk = conn.recv(length - len(msg))
        msg += chunk
    return msg