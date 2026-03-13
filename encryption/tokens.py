# encryption/tokens.py
import secrets


def generate_token(length: int = 32) -> str:
    """
    Generates a secure, URL-safe token for subscriber QR identity.
    """
    return secrets.token_urlsafe(length)
