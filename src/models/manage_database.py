import sqlite3

DATABASE_PATH = "database.db"
SQL_SCRIPT_PATH = "dbBot.sql"

def import_sql_script():
    """Виконує SQL-скрипт у базі даних."""
    with sqlite3.connect(DATABASE_PATH) as conn:
        with open(SQL_SCRIPT_PATH, "r", encoding="utf-8") as sql_file:
            sql_script = sql_file.read()
            conn.executescript(sql_script)
        print("SQL script imported successfully.")

import_sql_script()
