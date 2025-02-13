import threading
import socket

class Client:
    def __init__(self, addr, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.bind((addr, port))
        self.buffsize = 2048
    def send_data(self, conn, data):
        conn.sendall(data.encode('utf-8'))
    def recv_data(self, conn):
        while True:
          return conn.recv(self.buffsize).decode('utf-8')
    def start_listen(self):
        self.client.listen(1)
        conn, addr = self.client.accept()
        threading.Thread(target=self.send_data, args=(conn, 'ciao')).start()
        threading.Thread(target=self.recv_data, args=(conn,)).start()
    def start_connect(self, addr, port):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((addr, port))
        threading.Thread(target=self.send_data, args=(sock, 'ciao')).start()
        threading.Thread(target=self.recv_data, args=(sock,)).start()

if __name__ == '__main__':
    client = Client('192.168.1.53', 4444)
    client.start_listen()
    threading.Thread(target=client.start_connect, args=('192.168.1.21', 4444)).start() 
