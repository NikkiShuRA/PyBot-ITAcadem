import os
import subprocess
import sys
from urllib.parse import urlparse

from src.pybot.core.config import get_settings


# Парсер URL для установки пути к БД
def find_file_db(database_url: str) -> str:
    url = database_url
    parsed = urlparse(url)
    db_path = parsed.path.lstrip("/")
    name = db_path.split("/")[-1]
    location = "/".join(db_path.split("/")[:-1]) or "."
    full_path = os.path.join(location, name)
    return full_path


# Удаление существующей БД -> запуск миграций -> заполнение БД -> запуск бота
def main() -> None:
    settings = get_settings()
    db_file = find_file_db(settings.database_url)
    if os.path.exists(db_file):
        print(f"Найдена БД: {db_file}")

        confirm = input("Удалить БД? (y/n): ").lower().strip()
        if confirm != "y":
            print("Отмена.")
            sys.exit(0)

        try:
            os.remove(db_file)
        except OSError as e:
            print(f"❌ Ошибка: {e}")
            sys.exit(1)

        if os.path.exists(db_file):
            print("❌ Файл БД не удалён!")
            sys.exit(1)

        print("✅ БД удалена")

    commands: list[list[str]] = [
        ["alembic", "upgrade", "head"],
        ["py", "fill_point_db.py"],
        ["py", "run.py"],
    ]

    for cmd in commands:
        print(f"\n{'=' * 50}")
        print(f"🚀 Команда: {' '.join(cmd)}")
        print("Вывод:")

        result = subprocess.run(cmd, check=False)  # noqa: S603

        print(f"Код возврата: {result.returncode}")
        if result.returncode != 0:
            print("❌ Команда упала!")
            sys.exit(1)


if __name__ == "__main__":
    main()
