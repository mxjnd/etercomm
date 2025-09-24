from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.shortcuts import print_formatted_text
from prompt_toolkit.patch_stdout import patch_stdout
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import InMemoryHistory
from colorama import Fore, Style, init
from inspect import cleandoc
from os import system
from shutil import which, get_terminal_size
from getpass import getpass

class CLI:
    def __init__(self, os=None):
        if os:
            self.clearcmd = "cls" if os == "w" else "clear"
            if self.clearcmd == "clear" and not which(self.clearcmd):
                self.clearcmd = None
        self.history = InMemoryHistory()

        self.COLORS = {
            "INFO": Fore.CYAN,
            "SUCCESS": Fore.GREEN,
            "WARNING": Fore.YELLOW,
            "ERROR": Fore.LIGHTRED_EX,
            "CRITICAL": Fore.MAGENTA,
        }

    def info(self, text: str) -> str:
        return f"{self.COLORS['INFO']}[?] {text}{Style.RESET_ALL}"

    def success(self, text: str) -> str:
        return f"{self.COLORS['SUCCESS']}[+] {text}{Style.RESET_ALL}"
    
    def warning(self, text: str) -> str:
        return f"{self.COLORS['WARNING']}[!] {text}{Style.RESET_ALL}"

    def error(self, text: str) -> str:
        return f"{self.COLORS['ERROR']}[-] {text}{Style.RESET_ALL}"

    def critical(self, text: str) -> str:
        return f"{self.COLORS['CRITICAL']}[!!!] {text}{Style.RESET_ALL}"
    
    def on_prompt(self, option: str, text: str):
        match option:
            case "INFO":
                print_formatted_text(HTML(f"<ansicyan>[?] {text}</ansicyan>"))
            case "SUCCESS":
                print_formatted_text(HTML(f"<ansigreen>[+] {text}</ansigreen>"))
            case "WARNING":
                print_formatted_text(HTML(f"<ansiyellow>[!] {text}</ansiyellow>"))
            case "ERROR":
                print_formatted_text(HTML(f"<ansired>[-] {text}</ansired>"))
            case "CRITICAL":
                print_formatted_text(HTML(f"<ansimagenta>[!!!] {text}</ansimagenta>"))

    def print_incoming(self, address: str, n: int):
        print_formatted_text(HTML(f"<ansimagenta>[!!!] connessione ricevuta da </ansimagenta><ansiyellow>{address}</ansiyellow><ansimagenta>, ID: </ansimagenta><ansiyellow>{n}</ansiyellow>"))

    def clear(self) -> None:
        if self.clearcmd:
            system(self.clearcmd)
        else:
            print("\n" * 100)

    def banner(self) -> None:
        art = """███████╗████████╗███████╗██████╗  ██████╗ ██████╗ ███╗   ███╗███╗   ███╗
                 ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██╔════╝██╔═══██╗████╗ ████║████╗ ████║
                 █████╗     ██║   █████╗  ██████╔╝██║     ██║   ██║██╔████╔██║██╔████╔██║
                 ██╔══╝     ██║   ██╔══╝  ██╔══██╗██║     ██║   ██║██║╚██╔╝██║██║╚██╔╝██║
                 ███████╗   ██║   ███████╗██║  ██║╚██████╗╚██████╔╝██║ ╚═╝ ██║██║ ╚═╝ ██║
                 ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝     ╚═╝╚═╝     ╚═╝
                 ////////////////////////////////// may the server protect you //////////"""
        print(cleandoc(art) + "\n")

    def separator(self) -> None:
        print("-" * get_terminal_size().columns)    

    def command_prompt(self, text: str) -> str:
        session = PromptSession(history=self.history)
        with patch_stdout():
            try:
                return session.prompt(text)
            except KeyboardInterrupt:
                exit(0)
        
    def secret_prompt(self) -> bytes:
        while True:
            key = getpass("Inserire la chiave: ")
            if key == getpass("Verificare la chiave: "):
                return key.encode()
            else:
                print(self.error("le chiavi non coincidono, riprovare."))
    
    def chat_prompt(self, peer_obj, sock=None) -> int:
        while True:
            try:
                with patch_stdout():
                    data = prompt("you > ")
                    if peer_obj.alive:
                        if data != "":
                            peer_obj.send_data(data, sock=sock)
                    else:
                        if data != "":
                            self.on_prompt("ERROR", "dati non inviati.")
                        self.separator()
                        peer_obj.kill_them_all(sock=sock)
                        return 1
            except KeyboardInterrupt:
                self.separator()
                peer_obj.kill_them_all(sock=sock)
                return 1
