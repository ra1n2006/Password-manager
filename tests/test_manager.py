import json
from unittest.mock import patch

from cryptography.fernet import Fernet

import password_manager.manager as manager_module
from password_manager.crypto import generate_salt, generateHashPassword
from password_manager.manager import PasswordManager
from password_manager.storage import JsonStorage


def test_unlock(tmp_path):
    storage = JsonStorage(str(tmp_path / "storage.json"))
    manager = PasswordManager(storage)
    manager._master_storage = tmp_path / "master.json"

    salt = generate_salt()
    password_hash = generateHashPassword("master123", salt)

    with open(manager._master_storage, "w", encoding="utf-8") as file:
        json.dump({"salt": salt.hex(), "master_hash": password_hash}, file)

    with patch.object(
        manager_module, "get_encryption_key", return_value=Fernet.generate_key()
    ):
        assert manager.unlock("master123") is True
        assert manager.unlock("wrong_password") is False


def test_initialize_does_not_overwrite_password(tmp_path):
    storage = JsonStorage(str(tmp_path / "storage.json"))
    manager = PasswordManager(storage)
    manager._master_storage = tmp_path / "master.json"

    manager._master_storage.write_text(
        '{"salt": "1234", "master_hash": "test_hash"}',
        encoding="utf-8",
    )

    with patch.object(manager_module, "getpass") as mocked_getpass:
        manager.initialize()

    mocked_getpass.assert_not_called()
    assert json.loads(manager._master_storage.read_text())["master_hash"] == "test_hash"


def test_add_list_get_and_delete(tmp_path):
    storage = JsonStorage(str(tmp_path / "storage.json"))
    manager = PasswordManager(storage)
    manager._master_storage = tmp_path / "master.json"

    salt = generate_salt()
    password_hash = generateHashPassword("master123", salt)

    with open(manager._master_storage, "w", encoding="utf-8") as file:
        json.dump({"salt": salt.hex(), "master_hash": password_hash}, file)

    key = Fernet.generate_key()

    with patch.object(manager_module, "get_encryption_key", return_value=key):
        manager.add_password("google", "my_password")

        assert "google" in manager.list_services()
        assert manager.get_password("google", "master123") == "my_password"

        manager.delete_password("google")

        assert "google" not in manager.list_services()


def test_passwords_are_not_saved_in_plaintext(tmp_path):
    storage_path = tmp_path / "storage.json"
    storage = JsonStorage(str(storage_path))
    manager = PasswordManager(storage)
    manager._master_storage = tmp_path / "master.json"

    salt = generate_salt()
    password_hash = generateHashPassword("master123", salt)

    with open(manager._master_storage, "w", encoding="utf-8") as file:
        json.dump({"salt": salt.hex(), "master_hash": password_hash}, file)

    key = Fernet.generate_key()

    with patch.object(manager_module, "get_encryption_key", return_value=key):
        manager.add_password("google", "my_password")

    storage_text = storage_path.read_text(encoding="utf-8")
    master_text = manager._master_storage.read_text(encoding="utf-8")

    assert "my_password" not in storage_text
    assert "master123" not in master_text