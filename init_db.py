"""Cria o banco MySQL e as tabelas do Lunara.

Uso:
    python init_db.py
"""
from __future__ import annotations

import sys

import pymysql

from config import Config


def create_database() -> None:
    connection = pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def create_tables() -> None:
    from app import create_app, db
    from app import models  # noqa: F401  (registra as tabelas no metadata)

    app = create_app()
    with app.app_context():
        db.create_all()
        tables = sorted(db.metadata.tables.keys())
        print("Tabelas prontas:", ", ".join(tables))


def main() -> int:
    print(f"Conectando em {Config.DB_USER}@{Config.DB_HOST}:{Config.DB_PORT} ...")
    try:
        create_database()
        create_tables()
    except Exception as error:  # noqa: BLE001
        print("Não foi possível preparar o banco:", error, file=sys.stderr)
        print(
            "Confira se o MySQL está rodando e se DB_USER/DB_PASSWORD no .env estão corretos.",
            file=sys.stderr,
        )
        return 1
    print(f"Banco `{Config.DB_NAME}` pronto para uso.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
