"""Точка входа в приложение, запускает консольный интерфейс"""

from password_manager.cli import cli

def main() -> None:
    try:
        cli()
    except KeyboardInterrupt:
        print("Работа завершена")


if __name__ == "__main__":
    main()
