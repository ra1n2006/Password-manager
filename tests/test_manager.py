import tempfile

from password_manager.manager import PasswordManager
from password_manager.storage import JsonStorage


def test_unlock():
    """При верном мастер-пароле unlock вернет True, при неверном - False"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = JsonStorage(temp_dir + "/master.json")

        manager.initialize("master123")

        assert manager.unlock("master123") is True
        assert manager.unlock("master456") is False


def test_initialize_only_once():
    """Инициализировать мастер-пароль можно только единожды"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = JsonStorage(temp_dir + "/master.json")

        assert manager.initialize("master123") is True

        original_data = manager._master_storage.load()

        assert manager.initialize("new_password") is False

        new_data = manager._master_storage.load()

        assert original_data == new_data


def test_add_list_get():
    """Проверка добавления пароля и получения сервисов"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = JsonStorage(temp_dir + "/master.json")

        manager.initialize("master123")
        manager.add_password("google", "555")

        services = manager.list_services()

        assert "google" in services
        assert manager.get_password("google", "master123") == "555"


def test_delete():
    """Пароль нормально удаляется"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage = JsonStorage(temp_dir + "/storage.json")
        manager = PasswordManager(storage)
        manager._master_storage = JsonStorage(temp_dir + "/master.json")

        manager.initialize("master123")
        manager.add_password("google", "555")
        manager.delete_password("google")

        assert "google" not in manager.list_services()


def test_passwords_are_encrypted():
    """Пароль шифруется при записи в json"""
    with tempfile.TemporaryDirectory() as temp_dir:
        storage_path = temp_dir + "/storage.json"
        master_path = temp_dir + "/master.json"

        storage = JsonStorage(storage_path)
        manager = PasswordManager(storage)
        manager._master_storage = JsonStorage(master_path)

        manager.initialize("master123")
        manager.add_password("google", "555")

        with open(storage_path, "r", encoding="utf-8") as file:
            storage_data = file.read()

        master_data = manager._master_storage.load()

        assert "my_password" not in storage_data
        assert "master123" not in str(master_data)

        assert master_data["master_hash"] != "master123"
