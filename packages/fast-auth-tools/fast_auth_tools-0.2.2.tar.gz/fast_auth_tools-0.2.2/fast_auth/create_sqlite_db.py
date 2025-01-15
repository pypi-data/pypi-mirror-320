import sqlite3
import sys
from pathlib import Path
from typing import Optional

from .create_user import run_create_user_with_event_loop
from .settings import settings


def create_user_table(db_path: Optional[Path] = None):
    if __name__ == "__main__":
        print(f"Creating `users` table in {db_path or settings.user_db_path}")
    SQL = """CREATE TABLE IF NOT EXISTS users (
        username text PRIMARY KEY,
        password text NOT NULL
    );"""

    db = sqlite3.connect(settings.user_db_path)
    cursor = db.cursor()
    cursor.execute(SQL)
    db.commit()
    if __name__ == "__main__":
        if input("Would you like to create a user? [Y/n]: ").strip().lower() in {
            "n",
            "no",
        }:
            return
        run_create_user_with_event_loop()
        print("Success!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    else:
        path = None
    create_user_table(path)
