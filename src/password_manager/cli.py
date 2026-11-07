"""Консольный интерфейс менеджера паролей"""

import re
import sys
from getpass import getpass

from .crypto import generate_password
from .manager import PasswordManager
from .storage import JsonStorage


def start_manager(password_manager: PasswordManager) -> bool:
    """Создание мастер-пароля или вход в менеджер."""

    if password_manager.check_master_password():
        password = getpass("Введите мастер-пароль: ")
    else:
        print("Мастер-пароль еще не создан.")

        password = getpass("Создайте мастер-пароль: ")
        confirmation = getpass("Повторите мастер-пароль: ")

        if password != confirmation:
            print("Пароли не совпадают")
            return False

        if not password_manager.initialize(password):
            return False

    if not password_manager.unlock(password):
        print("Неверный мастер-пароль")
        print("Работа завершена")
        return False

    print("Менеджер разблокирован")
    return True


def cli() -> None:
    """Функция, обрабатывающая команды из консоли,
    передающая введенные данные методам объекта класса PasswordManager"""

    print("Доступные команды: add, list, get <name>, delete <name>, exit")
    json_storage = JsonStorage("src/data/storage.json")
    password_manager = PasswordManager(json_storage)
    if not start_manager(password_manager):
        return
    while 1:
        cmd = input("Введите команду\n")
        if cmd == "add":
            service = input("Введите название сервиса\n").strip()
            choice = input("Сгенерировать пароль? (да/нет)\n").strip().lower()

            if choice == "да":
                password = generate_password()
                print(f"Сгенерированный пароль: {password}")
            else:
                password = input("Введите пароль\n")

            password_manager.add_password(service, password)

        elif cmd == "list":
            if not password_manager.list_services():
                print("сохраненных сервисов нет")
                continue
            print("Сервисы:")
            for service in password_manager.list_services():
                print(service)

        elif re.fullmatch(r"get\s+.+", cmd):
            name = re.fullmatch(r"get\s+(.+)", cmd).group(1).strip()
            master_password = getpass("Подтвердите мастер-пароль\n")
            print(password_manager.get_password(name, master_password))

        elif re.fullmatch(r"delete\s+.+", cmd):
            name = re.fullmatch(r"delete\s+(.+)", cmd).group(1).strip()
            print(password_manager.delete_password(name))
        elif cmd == "exit":
            print("Работа завершена")
            sys.exit()
        else:
            print("Неизвестная команда\n")
