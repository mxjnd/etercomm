from threading import enumerate as threads

def disable_core_dump(os: str, cli_obj):
    if os == "w":
            try:
                import ctypes
                SEM_NOGPFAULTERRORBOX = 0x0002
                ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)
                print(cli_obj.success(f"core dump disattivato."))
            except Exception as e:
                print(cli_obj.error(f"errore nella disattivazione del core dump: {e}"))
    elif os in ["l", "d"]:
            try:
                import resource
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
                print(cli_obj.success(f"core dump disattivato."))
            except Exception as e:
                print(cli_obj.error(f"errore nella disattivazione del core dump: {e}"))

def debug_threads(self):
    for thread in thread():
        print(f"Thread: {thread.name}, ID: {thread.ident}, Alive: {thread.is_alive()}")
