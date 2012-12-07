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


class Connection:
    cmd_list = ['connect', 'ping', 'pingd', 'quit', 'finish']

    def __init__(self, conn, addr, srv):
        self.conn = conn
        self.addr = addr
        self.srv = srv
        self.stop = threading.Event()
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def run(self):
        while not self.stop.wait(0):
            try:
                data = self.recv()
                if data and len(data.strip()):
                    cmd, cmd_args = self.parse_data(data)
                    if cmd in self.cmd_list and callable(getattr(self, cmd, None)):
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
        self.stop.set()
        self.conn.close()

    def terminate(self):
        self.stop.set()

    def send(self, data):
        logger.debug("sending: {}".format(repr(data)))
        snd_data = data.encode('utf-8')
        snd_length = int(len(snd_data)).to_bytes(4, 'big')
        self.conn.sendall(snd_length)
        self.conn.sendall(snd_data)

    def recv(self):
        rcv_length = int.from_bytes(self.conn.recv(4), 'big')
        rcv_data = self.conn.recv(rcv_length)
        if not rcv_data:
            logger.info("Connection closed by foreign host.")
            self.stop.set()
            return False
        data = rcv_data.decode('utf-8')
        logger.debug("received: {}".format(repr(data)))
        return data

    def parse_data(self, data):
        data_list = data.split('\n', 1)
        return data_list[0], data_list[1:]

    def connect(self, data):
        self.srv.multicast_message('connected\n{}'.format(
                ':'.join(map(str,  self.addr))
            ))

    def ping(self, data):
        self.send('pong')

    def pingd(self, data):
        self.send('pongd\n{}'.format(' '.join(data)))

    def quit(self, data):
        if data:
            self.srv.multicast_message('ackquit\n{}'.format(data))
        self.stop.set()

    def finish(self, data):
        self.stop.set()
        self.srv.terminate()


class Server:
    running = False
    connections = []
    connections_lock = threading.RLock()

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
            except socket.timeout:
                pass
            except (KeyboardInterrupt, InterruptedError):
                self.stop()
            else:
                client_connection = Connection(conn, addr, self)
                with self.connections_lock:
                    self.connections.append(client_connection)
        self.stop()

    def terminate(self):
        self.running = False

    def stop(self):
        self.running = False
        self.multicast_message('ackfinish')
        # self.ward_thread.join()
        with self.connections_lock:
            for conn in self.connections:
                conn.terminate()
                conn.thread.join()
                del conn
        self.socket.close()

    def multicast_message(self, msg):
        with self.connections_lock:
            for conn in self.connections:
                if not conn.stop.wait(0):
                    conn.send(msg)


if __name__ == '__main__':
    server = Server()
    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)
    server.run()
    sys.exit(0)
