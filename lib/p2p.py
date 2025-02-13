import socket

class Client:
  def __init__(self, addr, port):
    self.client = socket.socket(socket.SOCK_STREAM, socket.AF_INET)
    self.client.bind((addr, port))
  def connto(self, addr, port):
    self.client.connect((addr, port))
  def sendata(self, data):
    pass
    
class Server:
  def __init__(self, addr, port):
    self.server = socket.socket(socket.SOCK_STREAM, socket.AF_INET)
    self.client.bind((addr, port))
  def handle_newconn(self):
    pass
  def handle_recvdata(self, data):
    pass
