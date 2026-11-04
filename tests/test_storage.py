from password_manager.storage import JsonStorage


def test_add_and_load(tmp_path):
    file_path = tmp_path / "storage.json"
    storage = JsonStorage(str(file_path))

    storage.add("google", "encrypted_password")

    assert storage.load() == {"google": "encrypted_password"}


def test_delete(tmp_path):
    file_path = tmp_path / "storage.json"
    storage = JsonStorage(str(file_path))

    storage.add("google", "encrypted_password")
    storage.delete("google")

    assert storage.load() == {}


def test_is_empty(tmp_path):
    file_path = tmp_path / "storage.json"
    storage = JsonStorage(str(file_path))

    assert storage.is_empty()

    storage.add("google", "encrypted_password")

    assert not storage.is_empty()
