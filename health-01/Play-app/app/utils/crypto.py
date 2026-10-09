# pyrefly: ignore [missing-import]
"""
Minimal symmetric encryption helpers for patient PII (name, phone).
Uses Fernet (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.
Key is derived from SECRET_KEY so no extra env var is needed for the demo.
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from app.config import SECRET_KEY


def _get_fernet() -> Fernet:
    """Derive a stable 32-byte Fernet key from the app's SECRET_KEY."""
    raw = hashlib.sha256(SECRET_KEY.encode()).digest()
    key = base64.urlsafe_b64encode(raw)
    return Fernet(key)


def encrypt(plaintext: str) -> str:
    """Encrypt a string and return a URL-safe base64 token (stored in DB)."""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a stored ciphertext token and return the original string."""
    return _get_fernet().decrypt(ciphertext.encode()).decode()
