#!/usr/bin/env python3
"""Reset and reseed MySQL database using schema.sql and seed_data.sql.

Usage:
  python database/reset_db.py --schema database/schema.sql --seed database/seed_data.sql --env-file backend/.env
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mysql.connector


def parse_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def strip_delimiter_commands(sql: str) -> str:
    lines: list[str] = []
    for line in sql.splitlines():
        if line.strip().upper().startswith("DELIMITER "):
            continue
        lines.append(line)
    return "\n".join(lines)


def split_sql_statements(sql: str) -> list[str]:
    """Split SQL text into statements while respecting quoted strings."""
    statements: list[str] = []
    current: list[str] = []
    in_single = False
    in_double = False
    escaped = False

    for ch in sql:
        current.append(ch)

        if escaped:
            escaped = False
            continue

        if ch == "\\":
            escaped = True
            continue

        if ch == "'" and not in_double:
            in_single = not in_single
            continue

        if ch == '"' and not in_single:
            in_double = not in_double
            continue

        if ch == ";" and not in_single and not in_double:
            stmt = "".join(current).strip()
            if stmt:
                statements.append(stmt)
            current = []

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements


def execute_sql_file(conn: mysql.connector.MySQLConnection, sql_file: Path) -> None:
    sql = sql_file.read_text(encoding="utf-8")
    sql = strip_delimiter_commands(sql)

    cursor = conn.cursor()
    try:
        try:
            for _ in cursor.execute(sql, multi=True):
                pass
        except TypeError:
            # Fallback for connector variants whose cursor.execute does not accept multi=True.
            for statement in split_sql_statements(sql):
                cursor.execute(statement)
        conn.commit()
    finally:
        cursor.close()


def recreate_database(conn: mysql.connector.MySQLConnection, db_name: str) -> None:
    cursor = conn.cursor()
    try:
        escaped_db = db_name.replace("`", "``")
        cursor.execute(f"DROP DATABASE IF EXISTS `{escaped_db}`")
        cursor.execute(f"CREATE DATABASE `{escaped_db}`")
        cursor.execute(f"USE `{escaped_db}`")
        conn.commit()
    finally:
        cursor.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Reset and reseed MySQL database.")
    parser.add_argument("--schema", required=True, help="Path to schema.sql")
    parser.add_argument("--seed", required=True, help="Path to seed_data.sql")
    parser.add_argument("--env-file", default="backend/.env", help="Path to backend env file")
    args = parser.parse_args()

    schema_path = Path(args.schema).resolve()
    seed_path = Path(args.seed).resolve()
    env_path = Path(args.env_file).resolve()

    if not schema_path.exists():
        print(f"[ERROR] Schema file not found: {schema_path}")
        return 1
    if not seed_path.exists():
        print(f"[ERROR] Seed file not found: {seed_path}")
        return 1

    env_values = parse_env_file(env_path)
    db_host = env_values.get("MYSQL_HOST", "127.0.0.1")
    db_port = int(env_values.get("MYSQL_PORT", "3306"))
    db_user = env_values.get("MYSQL_USER", "root")
    db_password = env_values.get("MYSQL_PASSWORD", "")
    db_name = env_values.get("MYSQL_DATABASE", "inventory_db")

    print("[INFO] Connecting to MySQL...")
    try:
        conn = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            autocommit=False,
        )
    except mysql.connector.Error as exc:
        print(f"[ERROR] Could not connect to MySQL: {exc}")
        return 1

    try:
        print(f"[INFO] Recreating database: {db_name}")
        recreate_database(conn, db_name)

        print(f"[INFO] Applying schema: {schema_path}")
        execute_sql_file(conn, schema_path)
        print(f"[INFO] Applying seed data: {seed_path}")
        execute_sql_file(conn, seed_path)
        print("[OK] Database schema and seed data applied successfully.")
        return 0
    except mysql.connector.Error as exc:
        print(f"[ERROR] Database reset failed: {exc}")
        return 1
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
