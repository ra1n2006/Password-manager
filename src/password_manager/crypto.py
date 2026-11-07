"""Набор функций для шифрования и хэширования"""

import base64
import hashlib
import secrets
import string

from cryptography.fernet import Fernet


def get_encryption_key(password: str, salt: bytes) -> bytes:
    """Получение ключа шифрования из мастер-пароля."""

    key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        600_000,
        dklen=32,
    )

    return base64.urlsafe_b64encode(key)


def generate_salt() -> bytes:
    """Функция, генерирующая соль для хэша"""

    return secrets.token_bytes(16)


def generate_hash_password(password: str, salt: bytes) -> str:
    """Функция, генерирующая хэш для пароля, с учетом соли"""

    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 600_000
    ).hex()


def generate_password() -> str:
    """Генерация надежного пароля."""

    alphabet = string.ascii_letters + string.digits + string.punctuation
    return "".join(secrets.choice(alphabet) for _ in range(24))


def encrypt_password(password: str, key: bytes) -> str:
    """Функция, реализующая шифрование пароля ключом из .env файла"""
    return Fernet(key).encrypt(password.encode("utf-8")).decode("utf-8")


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Функция, реализующая расшифрование пароля ключом из .env файла"""
    return (
        Fernet(key).decrypt(encrypted_password.encode("utf-8")).decode("utf-8")
    )
