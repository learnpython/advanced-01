# coding=utf-8

import argparse


def parse_arguments():
    parser = argparse.ArgumentParser(description='Server')
    parser.add_argument('--host', help="Server host", default='')
    parser.add_argument('--port', help="Server port", default=50007, type=int)
    parser.add_argument('--withlog', help="Logging level", action='store_true')
    return parser.parse_args()
