import json
import tempfile
from pathlib import Path

from password_manager.manager import PasswordManager
from password_manager.storage import JsonStorage


def test_unlock():
    """При верном мастер-пароле unlock вернет True, при неверном - False"""

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = Path(temp_dir + "/master.json")

        manager.initialize("master123")

        assert manager.unlock("master123") is True
        assert manager.unlock("master456") is False


def test_initialize_only_once():
    """Инициализировать мастер-пароль можно только единожды"""

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = Path(temp_dir + "/master.json")

        assert manager.initialize("master123") is True

        with open(manager._master_storage, "r", encoding="utf-8") as file:
            original_data = file.read()

        assert manager.initialize("new_password") is False

        with open(manager._master_storage, "r", encoding="utf-8") as file:
            new_data = file.read()

        assert original_data == new_data


def test_add_list_get():
    """Проверка добавления пароля и получения сервисов"""

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = Path(temp_dir + "/master.json")

        manager.initialize("master123")
        manager.add_password("google", "my_password")

        services = manager.list_services()

        assert "google" in services
        assert manager.get_password("google", "master123") == "my_password"


def test_delete():
    """Пароль нормально удаляется"""

    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)

        manager.add_password("google", "my_password")
        manager.delete_password("google")

        assert "google" not in manager.list_services()


def test_passwords_are_encrypted():
    """Пароль хэшируется при записи в json"""

    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = temp_dir + "/storage.json"
        master_path = Path(temp_dir + "/master.json")

        storage = JsonStorage(storage_path)
        manager = PasswordManager(storage)
        manager._master_storage = master_path

        manager.initialize("master123")
        manager.add_password("google", "my_password")

        with open(storage_path, "r", encoding="utf-8") as file:
            storage_data = file.read()

        with open(master_path, "r", encoding="utf-8") as file:
            master_data = file.read()

        assert "my_password" not in storage_data
        assert "master123" not in master_data

        master_json = json.loads(master_data)
        assert "master_hash" in master_json
        assert master_json["master_hash"] != "master123"
