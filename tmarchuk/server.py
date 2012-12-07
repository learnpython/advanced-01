#!/usr/bin/env python
# -*- coding:utf-8 -*-
import logging
import signal
import socket
import sys
import threading


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('server')


def sig_handler(signum, frame):
    global server
    if server and getattr(server, 'running'):
        server.stop()


class Connection(threading.Thread):
    cmd_list = []
    CHUNK_SIZE = 1024

    def __init__(self, conn, addr):
        self.conn = conn
        self.addr = addr
        self.stop = threading.Event()
        threading.Thread.__init__(self)

    def terminate(self):
        self.stop.set()

    def run(self):
        while not self.stop.wait(0):
            try:
                data = self.recv()
                if data and len(data.strip()):
                    cmd, cmd_args = self.parse_data(data)
                    if cmd in self.cmd_list and callable(getattr(self, cmd)):
                        getattr(self, cmd)(cmd_args)
                    else:
                        self.send('No such command')
            except socket.error as e:
                logger.info("Socket error: {}, {}".format(e.errno, e.strerror))
                break
            except IOError as e:
                if e.errno == 32:
                    logger.info("Connection closed by foreign host.")
                else:
                    logger.info("IO error: {}, {}".format(e.errno, e.strerror))
                break
        self.conn.close()

    def send(self, data):
        logger.debug("sending: {}".format(repr(data)))
        snd_data = data.encode('utf-8')
        self.conn.sendall(snd_data)

    def recv(self):
        rcv_data = self.conn.recv(self.CHUNK_SIZE)
        if not rcv_data:
            logger.info("Connection closed by foreign host.")
            self.terminate()
            return False
        data = rcv_data.decode('utf-8')
        logger.debug("received: %s".format(repr(data)))
        return data

    def parse_data(self, data):
        data_list = data.split()
        return data_list[0], data_list[1:]


class Server:
    running = False
    connections = []

    def __init__(self, host='', port=39999):
        logger.info("Init server at {}:{}".format(host, port))
        self.host = host
        self.port = int(port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(10)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        try:
            self.socket.bind((self.host, self.port))
            self.socket.listen(5)
        except socket.error as e:
            logger.info("Can't bind server, error: {}, {}".format(e.errno, e.strerror))
            sys.exit(2)

    def run(self):
        self.running = True
        while self.running:
            try:
                conn, addr = self.socket.accept()
            except (socket.timeout, InterruptedError):
                pass
            else:
                th_connection = Connection(conn, addr)
                th_connection.start()
                self.connections.append(th_connection)

    def stop(self):
        self.running = False
        self.socket.close()
        for conn in self.connections:
            conn.terminate()
            conn.join()
            del conn


if __name__ == '__main__':
    server = Server()
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    server.run()
    sys.exit(0)
