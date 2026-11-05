"""Класс, объект которого выполняет основную логику,
связанную с взаимодействием с хранилищем"""

import hmac
import json
from pathlib import Path

from .crypto import (
    decrypt_password,
    encrypt_password,
    generate_hash_password,
    generate_salt,
    get_encryption_key,
)
from .storage import JsonStorage


class PasswordManager:
    def __init__(self, storage: JsonStorage) -> None:
        self._storage = storage
        self._master_storage = Path("src/data/master.json")
        if not self._master_storage.exists():
            self._master_storage.parent.mkdir(parents=True, exist_ok=True)

            with self._master_storage.open("w", encoding="utf-8") as file:
                json.dump({}, file)
        self._master_key: bytes | None = None

    def initialize(self, password: str) -> bool:
        """Создание мастер-пароля, если он еще не задан."""

        if self.check_master_password():
            print("Мастер-пароль уже настроен.")
            return False

        if not password:
            print("Мастер-пароль не может быть пустым.")
            return False

        salt = generate_salt()
        password_hash = generate_hash_password(password, salt)

        with self._master_storage.open("w", encoding="utf-8") as file:
            json.dump({"salt": salt.hex(), "master_hash": password_hash}, file)

        print("Мастер-пароль настроен.")
        return True

    def unlock(self, master_password: str) -> bool:
        """Проверка мастер-пароля"""

        with self._master_storage.open("r", encoding="utf-8") as file:
            master_key = json.load(file)

        salt = bytes.fromhex(master_key["salt"])
        stored_hash = master_key["master_hash"]
        password_hash = generate_hash_password(master_password, salt)

        if not hmac.compare_digest(stored_hash, password_hash):
            return False

        self._master_key = get_encryption_key()
        return True

    def check_master_password(self) -> bool:
        """Проверка, настроен ли мастер-пароль"""

        if not self._master_storage.exists():
            return False

        with self._master_storage.open("r", encoding="utf-8") as file:
            data = json.load(file)

        return bool(data.get("salt") and data.get("master_hash"))

    def add_password(self, service: str, password: str) -> None:
        """Добавление в json-файл сервиса и его пароля в зашифрованном виде"""

        self._storage.load()
        self._storage.add(
            service, encrypt_password(password, get_encryption_key())
        )

    def list_services(self) -> dict[str, str]:
        """Вывести все сервисы, которые хранятся"""

        return self._storage.load()

    def get_password(self, service: str, master: str) -> str:
        """Получить пароль конкретного сервиса
        после подтверждения мастер-ключом"""

        if not self.unlock(master):
            return "Неверный мастер-пароль"

        if self._storage.load().get(service):
            return decrypt_password(
                self._storage.load()[service], get_encryption_key()
            )

        return "сервис с таким именем не найден"

    def delete_password(self, service: str) -> str:
        """Удалить сервис и его пароль из json-файла"""

        self._storage.load()
        if self._storage.load().get(service):
            self._storage.delete(service)
            return "сервис успешно удалён"
        else:
            return "сервис с таким именем не найден"
