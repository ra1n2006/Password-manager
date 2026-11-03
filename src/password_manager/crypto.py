import hashlib
import os
import secrets
import string
from pathlib import Path

from cryptography.fernet import Fernet
from dotenv import load_dotenv


def generate_salt() -> bytes:
    """Функция, генерирующая соль для хэша"""

    return secrets.token_bytes(16)


def generateHashPassword(password: str, salt: bytes) -> str:
    """Функция, генерирующая хэш для пароля, с учетом соли"""

    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 600_000).hex()


def generate_password() -> str:
    """Генерация надежного пароля."""

    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(16))


def get_encryption_key() -> bytes:
    """Функция, реализующая получение ключа шифрования из .env файла или его создание (в случае отсутствия)"""
    env_path = Path(".env")
    load_dotenv(env_path)

    key = os.getenv("ENCRYPTION_KEY")

    if key is None:
        key = Fernet.generate_key().decode("utf-8")

        with env_path.open("a", encoding="utf-8") as file:
            file.write(f"\nENCRYPTION_KEY={key}\n")

    return key.encode("utf-8")


def encrypt_password(password: str, key: bytes) -> str:
    """Функция, реализующая шифрование пароля ключом из .env файла"""
    return Fernet(key).encrypt(password.encode("utf-8")).decode("utf-8")


def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Функция, реализующая расшифрование пароля ключом из .env файла"""
    return Fernet(key).decrypt(encrypted_password.encode("utf-8")).decode("utf-8")
