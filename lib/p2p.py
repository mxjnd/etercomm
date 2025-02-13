import socket
import ssl
from threading import Thread

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
        contex = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        contex.load_cert_chain(keyfile=r'C:\Users\salvo\Documents\py\etercomm\etercomm\lib\key.pem', certfile=r'C:\Users\salvo\Documents\py\etercomm\etercomm\lib\cert.pem')
        conn, addr = listener.accept()
        tls = contex.wrap_socket(conn)
    def connect_to(self, addr, port):
        connection = socket.create_connection((addr, port))
        contex = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        contex.load_cert_chain(keyfile=r'C:\Users\salvo\Documents\py\etercomm\etercomm\lib\key.pem', certfile=r'C:\Users\salvo\Documents\py\etercomm\etercomm\lib\cert.pem')
        tls = contex.wrap_socket(connection, addr)
        return tls

if __name__ == '__main__':
    peer = Peer()
    conn = peer.listen_at('192.168.1.53', 4444)
    peer.connect_to('192.168.1.21', 4444)
    Thread(target=peer.recv_data, args=(conn,))
    peer.send_data(conn, 'hey')
