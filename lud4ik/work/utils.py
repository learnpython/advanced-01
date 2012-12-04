import random
import hashlib


def format_reply(reply):
    return bytes("{:4}{}".format(len(reply), reply), 'utf-8')


def get_random_hash(n=10):
    _str = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    random_name = ''.join([random.choice(_str) for i in range(n)])
    return hashlib.sha224(random_name.encode('utf-8')).hexdigest()
