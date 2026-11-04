"""Класс, преодставляющий взаимодействие с json-файлами"""

import json
from pathlib import Path


class JsonStorage:
    def __init__(self, file_path: str) -> None:
        self._file_path = Path(file_path)
        self._data: dict[str, str] = {}
        if not self._file_path.exists():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            with self._file_path.open("w", encoding="utf-8") as file:
                json.dump({}, file)
        self.load()

    def load(self) -> dict[str, str]:
        """Выгрузка всех пар сервис-зашифрованный пароль из json файла"""

        if not self._file_path.exists():
            self._data = {}
            return self._data

        with self._file_path.open("r", encoding="utf-8") as file:
            content = file.read()

        if not content.strip():
            self._data = {}
            return self._data

        self._data = json.loads(content)
        return self._data

    def persist(self) -> None:
        """Сериализация словаря с паролями и запись его в json файл"""

        with self._file_path.open("w", encoding="utf-8") as file:
            json.dump(self._data, file)

    def add(self, service_name: str, encrypted_password: str) -> None:
        """записать пару ключ-значение в json файл"""

        self._data[service_name] = encrypted_password
        self.persist()

    def delete(self, service_name: str):
        """Удаление пары ключ-значение из json файла"""

        self._data.pop(service_name)
        self.persist()

    def is_empty(self) -> bool:
        """Проверка на то, есть данные в json файле"""

        return not self._data
