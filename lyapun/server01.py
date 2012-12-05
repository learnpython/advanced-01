# coding=utf-8

import logging

from work.cmdargs import parse_arguments
from work.server import Server

args = parse_arguments()

logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] (%(threadName)s) %(message)s',
)

if not args.withlog:
    logging.disable(logging.CRITICAL)

HOST = args.host
PORT = args.port

server = Server(HOST, PORT)
server.run()
