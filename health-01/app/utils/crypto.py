"""
utils/crypto.py — Symmetric encryption helpers for patient PII (name, phone, email).

Uses Fernet (AES-128-CBC + HMAC-SHA256) from the `cryptography` package.
Dedicated FERNET_KEY is loaded independently from environment variables.
MultiFernet provides seamless backward-compatible decryption for legacy
records while encrypting all new records strictly with FERNET_KEY.
"""
import base64
import hashlib
from cryptography.fernet import Fernet, MultiFernet
from app.config import Config


def _get_fernet() -> MultiFernet:
    """
    Return a MultiFernet instance prioritizing the dedicated FERNET_KEY,
    with fallback decryption support for legacy SECRET_KEY-derived ciphertexts.
    """
    keys = []

    # 1. Primary dedicated FERNET_KEY (must be valid 32 url-safe base64 bytes)
    dedicated_key = getattr(Config, "FERNET_KEY", None) or ""
    if dedicated_key and len(dedicated_key.strip()) >= 32:
        try:
            keys.append(Fernet(dedicated_key.strip().encode()))
        except Exception:
            pass

    # 2. Backward compatibility fallback: derived key from SECRET_KEY
    secret = getattr(Config, "SECRET_KEY", "dev-secret-key-please-change-in-production")
    raw = hashlib.sha256(secret.encode()).digest()
    legacy_key = base64.urlsafe_b64encode(raw)
    keys.append(Fernet(legacy_key))

    return MultiFernet(keys)


def encrypt(plaintext: str) -> str:
    """Encrypt a string and return a URL-safe base64 token (stored in DB)."""
    if not plaintext:
        return ""
    return _get_fernet().encrypt(plaintext.encode()).decode()


def decrypt(ciphertext: str) -> str:
    """Decrypt a stored ciphertext token and return the original string."""
    if not ciphertext:
        return ""
    try:
        return _get_fernet().decrypt(ciphertext.encode()).decode()
    except Exception:
        return "[Decryption Error]"
