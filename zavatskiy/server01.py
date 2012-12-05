import socket
import logging
import threading


class Server01:

    def __init__(self, host='127.0.0.1', port=6666, max_queue=1):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind((host, port))
        self.socket.listen(max_queue)
        self.threads = []
        self.__shutdown = False

    def new_stream(self, conn, addr):
        """ Make thread for each client connection """
        t = threading.Thread(target=self.handle_request, args=(conn, addr))
        t.start()
        self.threads.append(t)

    def handle_request(self, conn, addr):
        """ Handler request """
        while True:
            data = conn.recv(1024)
            if not data: break
            conn.sendall(data)
        conn.close()

    def serve(self):
        """ Run server """
        self.__shutdown = False

        while not self.__shutdown:
            conn, addr = self.socket.accept()
            self.new_stream(conn, addr)
        self.shutdown()

    def shutdown(self):
        """ Shutdown server """
        self.__shutdown = True

        for thread in self.threads:
            thread.join()
        self.socket.close()

if __name__ == '__main__':

    server = Server01()
    server.serve()
