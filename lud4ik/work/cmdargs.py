import argparse


def get_cmd_args():
    parser = argparse.ArgumentParser(prog='sockets')
    parser.add_argument('-host', default='', help='host')
    parser.add_argument('-port', default=50007, type=int, help='port')
    args = parser.parse_args()
    return args