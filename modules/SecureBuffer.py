from sys import platform
import ctypes

class SecureBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = (ctypes.c_char * size)()
        self.locked = False
        self._lock_memory()
    
    def _lock_memory(self):
        if platform.startswith("linux") or platform.startswith("darwin"):
            libc = ctypes.CDLL("libc.so.6")
            result = libc.mlock(ctypes.byref(self.buffer), ctypes.c_size_t(self.size))
            if result != 0:
                raise RuntimeError("mlock failed")
        elif platform.startswith("win"):
            kernel32 = ctypes.windll.kernel32
            if not kernel32.VirtualLock(ctypes.byref(self.buffer), ctypes.c_size_t(self.size)):
                raise RuntimeError("VirtualLock failed")
        self.locked = True
    
    def unlock(self):
        if not self.locked:
            return
        if platform.startswith("linux") or platform.startswith("darwin"):
            libc = ctypes.CDLL("libc.so.6")
            libc.munlock(ctypes.byref(self.buffer), ctypes.c_size_t(self.size))
        elif platform.startswith("win"):
            kernel32 = ctypes.windll.kernel32
            kernel32.VirtualUnlock(ctypes.byref(self.buffer), ctypes.c_size_t(self.size))
        self.locked = False

    def write(self, data: bytes):
        if len(data) > self.size:
            raise ValueError("data too large")
        ctypes.memmove(self.buffer, data, len(data))

    def read(self):
        return bytes(self.buffer[:self.size])
    
    def clear(self):
        ctypes.memset(self.buffer, 0, self.size)

    def __del__(self):
        self.clear()
        self.unlock()
