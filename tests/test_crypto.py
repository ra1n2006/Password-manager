import pytest
from cryptography.fernet import Fernet, InvalidToken

from password_manager.crypto import (
    decrypt_password,
    encrypt_password,
    generate_hash_password,
    generate_salt,
    get_encryption_key,
)


def test_encrypt_and_decrypt_password() -> None:
    """Пароль, зашифрованный одним ключом, должен быть расшифрован им же."""
    key = Fernet.generate_key()
    password = "Danil007"

    encrypted = encrypt_password(password, key)

    assert encrypted != password
    assert decrypt_password(encrypted, key) == password


def test_wrong_key_cannot_decrypt_password() -> None:
    """Пароль нельзя расшифровать другим ключом."""
    key = Fernet.generate_key()
    wrong_key = Fernet.generate_key()
    password = "Danil007"

    encrypted = encrypt_password(password, key)

    with pytest.raises(InvalidToken):
        decrypt_password(encrypted, wrong_key)


def test_master_password_hash_is_repeatable_with_same_salt() -> None:
    """Одинаковые пароль и соль дают одинаковый хэш."""
    salt = generate_salt()

    first_hash = generate_hash_password("MasterPassword123!", salt)
    second_hash = generate_hash_password("MasterPassword123!", salt)

    assert first_hash == second_hash


def test_master_password_hash_changes_with_password() -> None:
    """Разные пароли с одинаковой солью дают разные хэши."""
    salt = generate_salt()

    first_hash = generate_hash_password("FirstPassword123!", salt)
    second_hash = generate_hash_password("SecondPassword123!", salt)

    assert first_hash != second_hash


def test_encryption_key_is_repeatable_with_same_password_and_salt() -> None:
    """Одинаковые пароль и соль дают одинаковый ключ шифрования."""
    salt = generate_salt()
    password = "MasterPassword123!"

    first_key = get_encryption_key(password, salt)
    second_key = get_encryption_key(password, salt)

    assert first_key == second_key


def test_encryption_key_changes_with_salt() -> None:
    """Разные соли дают разные ключи шифрования."""
    password = "MasterPassword123!"

    first_key = get_encryption_key(password, generate_salt())
    second_key = get_encryption_key(password, generate_salt())

    assert first_key != second_key


def test_encryption_key_can_encrypt_and_decrypt() -> None:
    """Полученный из мастер-пароля ключ подходит для Fernet."""
    password = "MasterPassword123!"
    salt = generate_salt()

    key = get_encryption_key(password, salt)
    encrypted = encrypt_password("Danil007", key)

    assert decrypt_password(encrypted, key) == "Danil007"
