"""
Password hashing utilities using bcrypt via ``passlib``.

Usage
-----
::

    from app.utils.hashing import hash_password, verify_password

    hashed = hash_password("my-secret-password")
    assert verify_password("my-secret-password", hashed)
"""

from passlib.context import CryptContext

# bcrypt context – rounds default to 12 which gives a good
# security / performance balance on modern hardware.
_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    Parameters
    ----------
    password:
        The user-supplied plaintext password.

    Returns
    -------
    str
        The bcrypt hash string (including algorithm identifier and salt).
    """
    return _pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Verify a plaintext password against a stored bcrypt hash.

    Parameters
    ----------
    plain:
        The user-supplied plaintext password to verify.
    hashed:
        The stored bcrypt hash to compare against.

    Returns
    -------
    bool
        ``True`` if the password matches, ``False`` otherwise.
    """
    return _pwd_context.verify(plain, hashed)
