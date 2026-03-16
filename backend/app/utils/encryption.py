"""
Field-level encryption using the ``cryptography`` library's Fernet (AES-128-CBC + HMAC-SHA256).

The ``ENCRYPTION_KEY`` setting is a 64-character hex string (32 raw bytes).
Those bytes are base64url-encoded to produce the 44-character Fernet key that
the ``cryptography`` library expects.

Usage
-----
::

    from app.utils.encryption import encrypt_field, decrypt_field

    ciphertext = encrypt_field("sensitive data")
    plaintext  = decrypt_field(ciphertext)
"""

import base64
import binascii

from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException, status

from app.config import settings


def _get_fernet() -> Fernet:
    """
    Derive a ``Fernet`` instance from the application's ``ENCRYPTION_KEY``.

    The hex-encoded 32-byte key is decoded to raw bytes and then
    base64url-encoded to meet Fernet's key format requirement.
    """
    raw_key: bytes = binascii.unhexlify(settings.ENCRYPTION_KEY)
    fernet_key: bytes = base64.urlsafe_b64encode(raw_key)
    return Fernet(fernet_key)


# Module-level singleton – created once per process.
_fernet: Fernet = _get_fernet()


def encrypt_field(value: str) -> str:
    """
    Encrypt a plaintext string using Fernet (AES-128-CBC + HMAC-SHA256).

    Parameters
    ----------
    value:
        The plaintext string to encrypt.

    Returns
    -------
    str
        URL-safe base64-encoded ciphertext (Fernet token).
    """
    token: bytes = _fernet.encrypt(value.encode("utf-8"))
    return token.decode("utf-8")


def decrypt_field(encrypted: str) -> str:
    """
    Decrypt a Fernet-encrypted string back to its original plaintext.

    Parameters
    ----------
    encrypted:
        The Fernet token produced by :func:`encrypt_field`.

    Returns
    -------
    str
        The original plaintext string.

    Raises
    ------
    HTTPException (400)
        If the token is invalid or has been tampered with.
    """
    try:
        plaintext: bytes = _fernet.decrypt(encrypted.encode("utf-8"))
        return plaintext.decode("utf-8")
    except (InvalidToken, Exception) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Decryption failed: invalid or tampered data",
        ) from exc
