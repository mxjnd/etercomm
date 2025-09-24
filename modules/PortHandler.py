from modules.Peer import Peer
from modules.CLI import CLI
import miniupnpc

class PortHandler:
    def __init__(self):
        self.cli = CLI()
        self.port = None
    
    def port_forward(self, local_port: int, external_port: int, protocol="TCP") -> None:
        upnp = miniupnpc.UPnP()
        upnp.discoverdelay = 200
        upnp.discover()
        upnp.selectigd()
        local_ip = upnp.lanaddr
        try:
            success = upnp.addportmapping(external_port, protocol, local_ip, local_port, "", "")
            if success:
                print(self.cli.success(f"port forwarding attivo: {external_port} -> {local_ip}:{local_port} ({protocol})"))
            else:
                print(self.cli.error("port forwarding fallito: effettuarlo manualmente all'indirizzo http://IP_LOCALE_DEL_TUO_ROUTER (https://portforward.com/router.htm)."))
                print(self.cli.info(f"mappare la porta esterna {external_port} al tuo indirizzo locale {local_ip} e alla porta {local_port} usata da Etercomm (protocollo {protocol})."))
                print(self.cli.warning("puoi continuare ad usare Etercomm verso host locali, ma non puoi comunicare fuori da questa LAN."))
        except Exception:
            print(self.cli.error("port forwarding fallito: effettuarlo manualmente all'indirizzo http://IP_LOCALE_DEL_TUO_ROUTER (https://portforward.com/router.htm)."))
            print(self.cli.info(f"mappare la porta esterna {external_port} del tuo router al tuo indirizzo locale {local_ip} e alla porta {local_port} usata da Etercomm (protocollo {protocol})."))
            print(self.cli.warning("puoi continuare ad usare Etercomm verso host locali, ma non puoi comunicare fuori da questa LAN se non effettui il port forwarding."))

    def print_info(self, external_port, local_port, local_ip, protocol="TCP") -> None:
        print(self.cli.info(f"mappare la porta esterna {external_port} del tuo router al tuo indirizzo locale {local_ip} e alla porta {local_port} usata da Etercomm (protocollo {protocol})."))

    def handle_port(self, peer_obj: Peer) -> None:
        while True:
            port = input(self.cli.success("scegliere una porta da utilizzare o premere invio per una casuale: "))
            if port.isdigit() or port == "":
                break
        if port != "":
            self.port = int(port)
            peer_obj.bind_local(port=self.port)
            self.print_info(self.port, self.port, peer_obj.get_local_ip())
        else:
            peer_obj.bind_local()
            if input(self.cli.success("effettuare un tentativo di port forwarding automatico tramite UPnP? (si / no | invio): ")).lower() == "si":
                self.port_forward(peer_obj.get_local_port(), peer_obj.get_local_port())
            else:
                self.print_info(peer_obj.get_local_port(), peer_obj.get_local_port(), peer_obj.get_local_ip())

    def rebind(self, peer_obj):
        peer_obj.bind_local(port=self.port if self.port is not None else None)
