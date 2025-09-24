from nacl.public import PrivateKey, PublicKey, Box
from argon2.low_level import hash_secret_raw, Type
from nacl.secret import SecretBox
from nacl.utils import random
from hashlib import scrypt

class Crypto:
    def __init__(self):
        self.private = PrivateKey.generate()
        self.public = self.private.public_key

    def encrypt_ASYM(self, data: bytes, remote_public: PublicKey) -> bytes:
        box = Box(self.private, remote_public)
        return box.encrypt(data)
    
    def decrypt_ASYM(self, data: bytes, remote_public: PublicKey) -> bytes:
        box = Box(self.private, remote_public)
        return box.decrypt(data)
    
    def make_public(self, key: bytes) -> PublicKey:
        return PublicKey(key)
    
    def derive_key(self, password: bytes, salt: bytes) -> bytes:
        return hash_secret_raw(secret=password, salt=salt, time_cost=3, memory_cost=65536, parallelism=2, hash_len=SecretBox.KEY_SIZE, type=Type.ID)
    
    def generate_salt(self, size: int) -> bytes:
        return random(size)
    
    def encrypt_SYM(self, data: bytes, key: bytes) -> bytes:
        box = SecretBox(key)
        return box.encrypt(data)
    
    def decrypt_SYM(self, data: bytes, key: bytes) -> bytes:
        box = SecretBox(key)
        return box.decrypt(data)
