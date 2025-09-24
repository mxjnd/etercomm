from modules.CLI import CLI
from modules.Peer import Peer
from modules.PortHandler import PortForwarding
from threading import Thread
from queue import Queue
from time import sleep

class Etercomm:
    def __init__(self):
        self.incoming_queue = Queue()
        self.chatting = False

    def start(self):
        cli = CLI()
        cli.clear()
        cli.banner()
        peer = Peer()
        print(cli.info(f"il tuo indirizzo IP pubblico è {peer.get_public_ip()}"))
        pw = PortForwarding()
        while True:
            port = input(cli.info("scegliere una porta da utilizzare o premere invio per una casuale: "))
            if port.isdigit():
                break
        if port != "":
            port = int(port)
            peer.bind_local(port=port)
            pw.print_info(port, port, peer.get_local_ip())
        else:
            peer.bind_local()
            if input(cli.info("effettuare un tentativo di port forwarding automatico tramite UPnP? (si / no | invio): ")).lower() == "si":
                pw.enable_port_forwarding(peer.get_local_port(), peer.get_local_port())
            else:
                pw.print_info(peer.get_local_port(), peer.get_local_port(), peer.get_local_ip())
        Thread(target=peer.incoming, args=(self.incoming_queue,), daemon=True).start()
        Thread(target=self.incoming_handler, daemon=True).start()
        while True:
            try:
                cmd = cli.prompt("etercomm $ ").split()
            except KeyboardInterrupt:
                exit(0)
            if len(cmd) > 1:
                if cmd[0] == "connect":
                    #try senno va in listen for accept anche in caso di errore
                    if input(cli.info("usare una pre-shared key simmetrica? (si / no | invio): ")).lower() == "si":
                        peer.load_psk(cli.secret())
                    try:
                        peer.connect_to(cmd[1], int(cmd[2]))
                    except:
                        pass
                    print(cli.info("in attesa di risposta..."))
                    peer.exchange(connecting=True)
                    accept = peer.accept_connection(connecting=True)
                    if accept == 0:
                        print(cli.info("connessione accettata.\n"))
                        self.chatting = True
                        Thread(target=peer.recv_data, daemon=True).start()
                        while True:
                            try:
                                if peer.alive:
                                    data = cli.prompt("you > ")
                                    peer.send_data(data)
                                else:
                                    peer.kill()
                                    break
                            except KeyboardInterrupt:
                                peer.kill()
                                break
                    elif accept == 1:
                        print(cli.error("connessione rifiutata.\n"))
                elif cmd[0] == "accept":
                    remote = self.connections[int(cmd[1])][0]
                    peer.exchange(connecting=False, sock=remote)
                    peer.accept_connection(connecting=False, sock=remote, accept=True)
                    print(cli.info("connessione accettata.\n"))
                    self.chatting = True
                    Thread(target=peer.recv_data, kwargs={'sock': remote}, daemon=True).start()
                    while True:
                        try:
                            if peer.alive:
                                data = cli.prompt("you > ")
                                peer.send_data(data, sock=remote)
                            else:
                                peer.kill()
                                break
                        except KeyboardInterrupt:
                            peer.kill()
                            break
                        except Exception as e:

                elif cmd[0] == "refuse": # aggiungere refuse persistente
                    remote = self.connections[int(cmd[1])][0]
                    peer.exchange(connecting=False, sock=remote)
                    peer.accept_connection(connecting=False, sock=remote, accept=False)
                    print(cli.error("connessione rifiutata.\n"))
            else:
                print(cli.error("comando non valido."))

    def incoming_handler(self):
        i = 0
        self.queue = Queue()
        self.connections = []
        while True:
            sleep(1.3)
            if not self.incoming_queue.empty() and not self.chatting:
                self.remote, self.address = self.incoming_queue.get()
                print(f"[!!!] connessione ricevuta da {self.address[0]}, ID: {i}")
                self.connections.append((self.remote, self.address))
                i += 1
            else:
                continue

if __name__ == "__main__":
    etercomm = Etercomm()
    etercomm.start()
