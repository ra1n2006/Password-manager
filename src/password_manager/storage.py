import json
from pathlib import Path


class JsonStorage:

    def __init__(self, file_path: str) -> None:
        self._file_path = Path(file_path)
        self._data: dict[str, str] = {}

    def load(self) -> dict[str, str]:
        if not self._file_path.exists():
            self._data = {}
            return self._data

        with self._file_path.open("r", encoding="utf-8") as file:
            loaded_data = json.load(file)

        self._data = loaded_data
        return self._data

    def persist(self) -> None:
        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file)

    def add(self, service_name: str, encrypted_password: str) -> None:
        self._data[service_name] = encrypted_password
        self.persist()

    def delete(self, service_name: str):
        self._data.pop(service_name)
        self.persist()

    def is_empty(self) -> bool:
        return not self._data

