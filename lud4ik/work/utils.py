import socket
import random
import hashlib
import logging
from inspect import signature
from contextlib import contextmanager


def format_reply(reply):
    byte_reply = bytes(reply, 'utf-8')
    return len(byte_reply).to_bytes(4, 'little') + byte_reply


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


def get_msg(conn):
    MSG_LEN = 4
    msg_len = int.from_bytes(get_conn_data(conn, MSG_LEN), 'little')
    msg = get_conn_data(conn, msg_len)
    return msg


def get_keyword_args(function):
    kwargs = []
    params = signature(function).parameters.values()
    for i in params:
        if i.kind == i.KEYWORD_ONLY:
            kwargs.append(i.name)
    return kwargs


def configure_logging(who):
    logging.basicConfig(
        filename = './tmp.log',
        level=logging.INFO,
        format= who +' [%(levelname)s] (%(threadName)s) %(message)s',
    )