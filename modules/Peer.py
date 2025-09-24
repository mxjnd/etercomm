from modules.Crypto import Crypto
from modules.CLI import CLI
from struct import pack, unpack
from hashlib import sha256
from requests import get
from time import sleep
from queue import Queue
from os import urandom
import socket
import json

class Peer:
    def __init__(self):
        self.listen_sock = None
        self.client_sock = None
        self.cli = CLI()
        self.crypto = None
        self.psk = None
        self.salt = None
        self.symmetric = False
        self.alive = True # ??
        self.MIN_SIZE = 1024
        self.MAX_SIZE = 6144
        self.MAX_PLAIN = self.MAX_SIZE - 4

    def get_public_ip(self) -> str:
        return get("https://api.ipify.org").text

    def get_local_ip(self) -> str:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("1.1.1.1", 80))
            return s.getsockname()[0]
        except Exception:
            return "127.0.0.1"

    def get_local_port(self) -> int:
        return self.listen_sock.getsockname()[1]

    def bind_local(self, port=None) -> None:
        self.listen_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listen_sock.bind((self.get_local_ip(), port if port else 0))
        self.listen_sock.listen(1)
        self.listen_sock.settimeout(1.0)

    def incoming_connections(self, queue: Queue) -> None:
        while True:
            try:
                conn, addr = self.listen_sock.accept()
                queue.put((conn, addr))
            except socket.timeout:
                continue
            except (OSError, AttributeError):
                break

    def connect_to(self, ipv4: str, port: int) -> None:
        if self.client_sock:
            try:
                self.client_sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.client_sock.close()
            except Exception:
                pass
        self.client_sock = None
        self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_sock.connect((ipv4, port))
        print(self.cli.success(f"connesso a {ipv4}:{port}"))
        self.remote_ipv4 = ipv4

    def send_data(self, data: str, sock=None) -> None:
        target_sock = sock if sock else self.client_sock
        if target_sock:
            data = self.make_data(data.encode())
            if data == 1:
                self.cli.on_prompt("ERROR", "messaggio troppo lungo.")
                return
            if self.symmetric:
                data = self.crypto.encrypt_SYM(data, self.psk)
            data = self.crypto.encrypt_ASYM(data, self.remote_public)
            target_sock.sendall(data)

    def recv_data(self, size=6144, sock=None) -> None:
        target_sock = sock if sock else self.client_sock
        target_sock.settimeout(1)
        while self.alive:
            try:
                data = target_sock.recv(size)
                if not data:
                    print("connessione terminata dall'host remoto, CTRL-C o invio per chiudere.")
                    break
                data = self.crypto.decrypt_ASYM(data, self.remote_public)
                if self.symmetric:
                    data = self.crypto.decrypt_SYM(data, self.psk)
                data = self.parse_data(data)
                print(f"{target_sock.getpeername()[0]} > {data.decode('utf-8')}")
            except (socket.timeout, BlockingIOError):
                continue
            except Exception:
                break
        self.alive = False

    def accept_connection(self, connecting=False, sock=None, accept=False) -> str | None:
        target_sock = sock if sock else self.client_sock
        target_sock.settimeout(5)
        if target_sock:
            if connecting == True:
                try:
                    if self.crypto.decrypt_ASYM(self.client_sock.recv(2048), self.remote_public).decode("utf-8") == "0":
                        return 0
                    else:
                        self.kill_them_all(sock=sock)
                        return 1
                except TimeoutError:
                    print(self.cli.error("tempo scaduto, ritentare la connessione."))
            elif connecting == False:
                sleep(1)
                if accept == True:
                    target_sock.sendall(self.crypto.encrypt_ASYM("0".encode(), self.remote_public))
                elif accept == False:
                    target_sock.sendall(self.crypto.encrypt_ASYM("1".encode(), self.remote_public))
                    self.kill_them_all(sock=sock)

    def exchange(self, connecting=False, sock=None, showkeys=True) -> None | int:
        target_sock = sock if sock else self.client_sock
        if target_sock:
            if not self.crypto:
                self.crypto = Crypto()
            if connecting == True:
                sleep(1)
                data = json.dumps({
                    "public": bytes(self.crypto.public).hex(),
                    "salt": bytes(self.salt).hex() if self.symmetric == True else None
                    })
                target_sock.sendall(data.encode())
                try:
                    data = json.loads(target_sock.recv(2048).decode("utf-8"))
                except Exception as e:
                    print(self.cli.error(f"errore nella connessione: {e}"))
                    return 1
                remote_public = bytes.fromhex(data["public"])
                if showkeys:
                    print(self.cli.warning(f"fingerprint della chiave pubblica locale: {self.fingerprint(self.crypto.public.encode())}"))
                    print(self.cli.warning(f"fingerprint della chiave pubblica remota: {self.fingerprint(remote_public)}"))
                self.remote_public = self.crypto.make_public(remote_public)
            elif connecting == False:
                data = json.loads(target_sock.recv(2048).decode("utf-8"))
                remote_public = bytes.fromhex(data["public"])
                if showkeys:
                    print(self.cli.warning(f"fingerprint della chiave pubblica locale: {self.fingerprint(self.crypto.public.encode())}"))
                    print(self.cli.warning(f"fingerprint della chiave pubblica remota: {self.fingerprint(remote_public)}"))
                self.remote_public = self.crypto.make_public(remote_public)
                self.salt = bytes.fromhex(data["salt"]) if data["salt"] is not None else None
                sleep(1)
                data = json.dumps({
                    "public": bytes(self.crypto.public).hex(),
                    "salt": None
                    })
                target_sock.sendall(data.encode())
                if self.salt is not None:
                    self.psk = self.crypto.derive_key(self.cli.secret_prompt(), self.salt)
                    self.symmetric = True

    def load_psk(self, key: bytes) -> None:
        if not self.crypto:
            self.crypto = Crypto()
        self.salt = self.crypto.generate_salt(16)
        self.psk = self.crypto.derive_key(key, self.salt)
        self.symmetric = True

    def fingerprint(self, public: bytes, blocks=6, digits=4) -> str:
        public_hash = sha256(public).digest()
        number = int.from_bytes(public_hash, "big")
        code = str(number).zfill(blocks * digits + 5)
        groups = [code[i:i + digits] for i in range(0, blocks * digits, digits)]
        return " ".join(groups)
    
    def make_data(self, data: bytes) -> bytes | int:
        if len(data) > self.MAX_PLAIN:
            return 1
        data = pack(">I", len(data)) + data
        return data + urandom(self.MAX_SIZE - len(data))
    
    def parse_data(self, data: bytes):
        length = unpack(">I", data[:4])[0]
        return data[4:4+length]

    def kill_them_all(self, sock=None) -> None:
        self.alive = False
        self.crypto = None
        self.symmetric = None
        if self.client_sock:
            try:
                self.client_sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.client_sock.close()
            except Exception:
                pass
            self.client_sock = None
        if self.listen_sock:
            try:
                self.listen_sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                self.listen_sock.close()
            except Exception:
                pass
            self.listen_sock = None
        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass
