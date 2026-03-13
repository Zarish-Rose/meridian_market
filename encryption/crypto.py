import os
import base64
from Crypto.Cipher import AES
from django.conf import settings


BLOCK_SIZE = 16  # AES block size


def _pad(s: bytes) -> bytes:
    padding = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + bytes([padding]) * padding


def _unpad(s: bytes) -> bytes:
    padding = s[-1]
    return s[:-padding]


def encrypt_value(value: str) -> str:
    if value is None:
        return None

    key = settings.ENCRYPTION_KEY.encode()  # 32 bytes for AES-256
    iv = os.urandom(16)

    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(_pad(value.encode()))

    return base64.b64encode(iv + encrypted).decode()


def decrypt_value(value: str) -> str:
    if value is None:
        return None

    raw = base64.b64decode(value)
    iv = raw[:16]
    encrypted = raw[16:]

    key = settings.ENCRYPTION_KEY.encode()
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = _unpad(cipher.decrypt(encrypted))

    return decrypted.decode()
