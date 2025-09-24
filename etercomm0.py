from modules.CLI import CLI
from modules.Peer import Peer
from modules.utils import *
from modules.PortHandler import PortHandler
from platform import system as getos
from threading import Thread, enumerate as tenumerate
from queue import Queue
from time import sleep

class Etercomm:
    def __init__(self):
        self.os = getos()[0].lower() # 'w'(indows) | 'l'(inux) | 'd'(macOS)
        self.cli = CLI(self.os)
        self.chatting = None

    def main(self):
        self.cli.clear()
        self.cli.banner()
        disable_core_dump(self.os, self.cli)
        self.peer = Peer()
        print(self.cli.success(f"il tuo indirizzo IP pubblico è {self.peer.get_public_ip()}"))
        self.port_handler = PortHandler()
        self.port_handler.handle_port(self.peer)
        Thread(target=self.incoming_handler, daemon=True).start()
        Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
        while True:
            # debug_threads()
            self.chatting = False
            cmd = self.cli.command_prompt("etercomm $ ").split()
            match cmd[0]:
                case "connect":
                    self.chatting = True
                    if len(cmd) != 3:
                        print(self.cli.error(f"comando non valido: connect [IP] [PORT]"))
                        continue
                    try:
                        remote_port = int(cmd[2])
                    except Exception:
                        print(self.cli.error(f"porta non valida."))
                        continue
                    if cmd[1] == self.peer.get_local_ip() and remote_port == self.port_handler.port:
                        print(self.cli.error(f"non puoi connetterti a te stesso."))
                        continue
                    if input(self.cli.success("usare una pre-shared key simmetrica? (si / no | invio): ")).lower() == "si":
                        self.peer.load_psk(self.cli.secret_prompt())
                    try:
                        self.peer.connect_to(cmd[1], remote_port)
                    except Exception as e:
                        print(self.cli.error(f"errore nella connessione: {e}"))
                        continue
                    print(self.cli.success("in attesa di risposta..."))
                    if self.peer.exchange(connecting=True) == 1:
                        continue
                    if self.peer.accept_connection(connecting=True) == 0:
                            print(self.cli.success("connessione accettata."))
                            self.cli.separator()
                            self.peer.alive = True
                            Thread(target=self.peer.recv_data, daemon=True).start()
                            if self.cli.chat_prompt(self.peer) == 1:
                                self.port_handler.rebind(self.peer)
                                Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
                    else:
                        print(self.cli.error("connessione rifiutata manualmente."))
                        Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
                case "accept":
                    self.chatting = True
                    if len(cmd) != 2:
                        print(self.cli.error(f"comando non valido: accept [ID]"))
                        continue
                    try:
                        cmd = int(cmd[1])
                        if cmd < self.i:
                            print(self.cli.error("connessione non più disponibile."))
                            continue
                        remote = self.connections[cmd][0]
                    except Exception:
                        print(self.cli.error("ID non valido."))
                        continue
                    self.peer.exchange(connecting=False, sock=remote)
                    self.peer.accept_connection(connecting=False, sock=remote, accept=True)
                    print(self.cli.success("connessione accettata."))
                    self.cli.separator()
                    self.peer.alive = True
                    Thread(target=self.peer.recv_data, kwargs={'sock': remote}, daemon=True).start()
                    if self.cli.chat_prompt(self.peer, sock=remote) == 1:
                        self.port_handler.rebind(self.peer)
                        Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
                case "refuse":
                    self.chatting = True
                    try:
                        i = int(cmd[1])
                        if i < self.i:
                            print(self.cli.error("connessione non più disponibile."))
                            continue
                        remote = self.connections[i][0]
                    except Exception:
                        print(self.cli.error("ID non valido."))
                        continue
                    self.peer.exchange(connecting=False, sock=remote)
                    self.peer.accept_connection(connecting=False, sock=remote, accept=False)
                    print(self.cli.success("connessione rifiutata."))
                    self.port_handler.rebind(self.peer)
                    Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
                case "block":
                    self.chatting = True
                    try:
                        i = int(cmd[1])
                        if i < self.i:
                            print(self.cli.error("connessione non più disponibile."))
                            continue
                        remote = self.connections[i][0]
                        address = self.connections[i][1][0]
                    except Exception:
                        print(self.cli.error("ID non valido."))
                        continue
                    self.peer.exchange(connecting=False, sock=remote)
                    self.peer.accept_connection(connecting=False, sock=remote, accept=False)
                    if address not in self.blocked:
                        self.blocked.append(address)
                    print(self.cli.success("connessione rifiutata e indirizzo bloccato."))
                    self.port_handler.rebind(self.peer)
                    Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
                case "unblock":
                    self.blocked.remove(address)
                case "exit":
                    exit(0)
                case "help":
                    pass
                case _:
                    print(self.cli.error("comando non valido."))

    def incoming_handler(self):
        self.incoming_queue = Queue()
        self.i = -1
        self.connections = []
        self.blocked = []
        while True:
            sleep(1.3)
            if not self.incoming_queue.empty() and not self.chatting:
                self.remote, self.address = self.incoming_queue.get()
                if self.address[0] not in self.blocked:
                    self.i += 1
                    self.cli.print_incoming(self.address[0], self.i)
                    self.connections.append((self.remote, self.address))
                else:
                    self.peer.exchange(connecting=False, sock=self.remote, showkeys=False)
                    self.peer.accept_connection(connecting=False, sock=self.remote, accept=False)
                    self.port_handler.rebind(self.peer)
                    Thread(target=self.peer.incoming_connections, args=(self.incoming_queue,), daemon=True).start()
            else:
                continue

if __name__ == "__main__":
    from colorama import init
    init(autoreset=False, convert=True)
    etercomm = Etercomm()
    etercomm.main()
