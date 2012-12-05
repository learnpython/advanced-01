# coding=utf-8

import signal
import socket
import threading
import logging

from work.general import recieve_data_from_socket
from work.utils import parse_recieved_bytes, prepare_data_for_sending

do_stop = False


class Server():

    threads = []

    def __init__(self, host, port):
        logging.info('Initialized server with host %s, port %d', host, port)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.sock.bind((host, port))

    def run(self):
        global do_stop
        while not do_stop:
            self.sock.listen(5)
            try:
                conn, addr = self.sock.accept()
                logging.info("Accepted conn=%s, addr=%s", conn, addr)
                self.handle_client(conn, addr)
            except InterruptedError:
                pass
            except socket.timeout:
                pass
        self.stop()

    def handle_client(self, conn, addr):
        thread = threading.Thread(
            target=Server.socket_handler, args=[self, conn, addr]
        )
        thread.start()
        self.threads.append(thread)

    def stop(self):
        global do_stop
        do_stop = True
        for thread in self.threads:
            logging.info(
                "thread=%s, thread.is_alive=%s", thread, thread.is_alive()
            )
            if thread.is_alive():
                thread.join()
        self.sock.close()
        logging.info("Socket closed, socket=%s", self.sock)

    @staticmethod
    def socket_handler(server, conn, addr):
        global do_stop
        conn.settimeout(1.0)
        while not do_stop:
            try:
                recieved_bytes = recieve_data_from_socket(conn)
            except socket.timeout:
                continue
            command, data = parse_recieved_bytes(recieved_bytes)
            logging.info("Command=%s, data=%s", command, data)
            if command == 'connect':
                conn.sendall(prepare_data_for_sending('connected'))
            elif command == 'ping':
                conn.sendall(prepare_data_for_sending('pong'))
            elif command == 'pingd':
                conn.sendall(prepare_data_for_sending('pongd ' + data))
            elif command == 'quit':
                if data:
                    conn.sendall(prepare_data_for_sending('ackquit ' + data))
                else:
                    conn.sendall(prepare_data_for_sending('ackquit'))
                conn.close()
                break
            elif command == 'finish':
                conn.sendall(prepare_data_for_sending('ackfinish'))
                conn.close()
                do_stop = True
                break
        else:
            conn.sendall(prepare_data_for_sending('ackfinish'))
            conn.close()

        server.threads.remove(threading.currentThread())
        logging.info("Thread off conn=%s", conn)


def kill_signal_handler(signum, frame):
    global do_stop
    do_stop = True
    logging.info("Kill signal handler, do_stop=%s", do_stop)

signal.signal(signal.SIGINT, kill_signal_handler)
