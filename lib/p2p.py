import socket

class Peer:
    def __init__(self):
        self.timeout = 0
        self.buffsize = 2048
        self.encoding = 'utf-8'
    def send_data(self, conn, data):
        conn.sendall(data.encode(self.encoding))
    def recv_data(self, conn):
        return conn.recv(self.buffsize).decode(self.encoding)
    def listen_at(self, addr, port):
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.bind((addr, port))
        listener.listen(1)
        return listener.accept()
    def connect_to(self, addr, port):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((addr, port))
        return connection

if __name__ == '__main__':
    pass
