"""Класс, объект которого выполняет основную логику,
связанную с взаимодействием с хранилищем"""

import hmac

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
        self._master_storage = JsonStorage("src/data/master.json")
        self._enc_key: bytes | None = None

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
        encryption_salt = generate_salt()
        self._enc_key = get_encryption_key(password, encryption_salt)

        self._master_storage._data = {
            "salt": salt.hex(),
            "master_hash": password_hash,
            "encryption_salt": encryption_salt.hex(),
        }
        self._master_storage.persist()

        print("Мастер-пароль настроен.")
        return True

    def unlock(self, master_password: str) -> bool:
        """Проверка мастер-пароля"""

        master_data = self._master_storage.load()

        salt = bytes.fromhex(master_data["salt"])
        encryption_salt = bytes.fromhex(master_data["encryption_salt"])

        stored_hash = master_data["master_hash"]

        password_hash = generate_hash_password(master_password, salt)

        if not hmac.compare_digest(stored_hash, password_hash):
            return False

        self._enc_key = get_encryption_key(
            master_password,
            encryption_salt,
        )

        return True

    def check_master_password(self) -> bool:
        """Проверка, настроен ли мастер-пароль"""
        data = self._master_storage.load()

        return bool(data.get("salt") and data.get("master_hash"))

    def add_password(self, service: str, password: str) -> None:
        """Добавление в json-файл сервиса и его пароля в зашифрованном виде"""
        if service.strip() == "":
            print("Имя сервиса не может быть пустым")
            return
        self._storage.load()
        self._storage.add(service, encrypt_password(password, self._enc_key))

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
                self._storage.load()[service], self._enc_key
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
