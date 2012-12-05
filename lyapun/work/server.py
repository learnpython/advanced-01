# coding=utf-8

import signal
import socket
import threading
import logging

from work.general import recieve_data_from_socket
from work.utils import parse_recieved_bytes, prepare_data_for_sending


class Server():

    do_stop = False

    def __init__(self, host, port):
        logging.info('Initialized server with host %s, port %d', host, port)
        signal.signal(signal.SIGINT, self.kill_signal_handler)
        self.threads = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(1.0)
        self.sock.bind((host, port))

    def run(self):
        while not self.do_stop:
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
            target=self.socket_handler, args=(conn, addr)
        )
        thread.start()
        self.threads.append(thread)

    def stop(self):
        self.do_stop = True
        for thread in self.threads:
            logging.info(
                "thread=%s, thread.is_alive=%s", thread, thread.is_alive()
            )
            thread.join()
        self.sock.close()
        logging.info("Socket closed, socket=%s", self.sock)

    def socket_handler(self, conn, addr):
        conn.settimeout(1.0)
        while not self.do_stop:
            try:
                recieved_bytes = recieve_data_from_socket(conn)
                command, data = parse_recieved_bytes(recieved_bytes)
                logging.info("Command=%s, data=%s", command, data)
            except socket.timeout:
                continue
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
                self.do_stop = True
                break
        else:
            conn.sendall(prepare_data_for_sending('ackfinish'))
            conn.close()

        self.threads.remove(threading.currentThread())
        logging.info("Thread off conn=%s", conn)

    def kill_signal_handler(self, signum, frame):
        self.do_stop = True
        logging.info("Kill signal handler, do_stop=%s", self.do_stop)
