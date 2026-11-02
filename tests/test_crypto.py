"""Тесты для функций шифрования и хэширования"""

import pytest
from cryptography.fernet import Fernet, InvalidToken

from password_manager.crypto import (
    decrypt_password,
    encrypt_password,
    generate_salt,
    generateHashPassword,
)


def test_encrypt_and_decrypt_password() -> None:
    """Пароль, зашифрованный одним ключом, должен быть расшифрован им же"""
    key = Fernet.generate_key()
    password = "Danil007"

    encrypted = encrypt_password(password, key)

    assert encrypted != password
    assert decrypt_password(encrypted, key) == password


def test_wrong_key_cannot_decrypt_password() -> None:
    """Пароль, зашифрованный одним ключом, не может быть расшифрован другим"""
    key = Fernet.generate_key()
    wrong_key = Fernet.generate_key()
    passwd1 = "Danil007"

    encrypted = encrypt_password(passwd1, key)

    with pytest.raises(InvalidToken):
        passwd2 = decrypt_password(encrypted, wrong_key)

        assert passwd2 != passwd1


def test_master_password_hash_is_repeatable_with_same_salt() -> None:
    """Один и тот же пароль и одна и та же соль выдают одинаковый хэш"""
    salt = generate_salt()

    first_hash = generateHashPassword("MasterPassword123!", salt)
    second_hash = generateHashPassword("MasterPassword123!", salt)

    assert first_hash == second_hash


def test_master_password_hash_changes_with_password() -> None:
    """Разные пароли и одинаковая соль выдают разный хэш"""
    salt = generate_salt()

    first_hash = generateHashPassword("FirstPassword123!", salt)
    second_hash = generateHashPassword("SecondPassword123!", salt)

    assert first_hash != second_hash
