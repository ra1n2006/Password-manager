import json
import tempfile
from pathlib import Path

from password_manager.storage import JsonStorage


def test_load():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "storage.json"

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump({"google": "password123"}, file)

        storage = JsonStorage(str(filepath))

        assert storage.load() == {"google": "password123"}


def test_persist():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "storage.json"
        storage = JsonStorage(str(filepath))

        storage._data = {"google": "password123"}
        storage.persist()

        with open(filepath, "r", encoding="utf-8") as file:
            data = json.load(file)

        assert data == {"google": "password123"}


def test_add():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "storage.json"
        storage = JsonStorage(str(filepath))

        storage.add("google", "password123")

        assert storage._data == {"google": "password123"}


def test_delete():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "storage.json"
        storage = JsonStorage(str(filepath))

        storage.add("google", "password123")
        storage.delete("google")

        assert storage._data == {}


def test_delete_missing_service():
    with tempfile.TemporaryDirectory() as temp_dir:
        filepath = Path(temp_dir) / "storage.json"
        storage = JsonStorage(str(filepath))
        try:
            storage.delete("google")
        except KeyError:
            pass
        else:
            assert False
