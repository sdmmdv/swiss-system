#!/usr/bin/env python3

import os
import psycopg2
import subprocess

def get_root():
    try:
        root = subprocess.check_output(['git', 'rev-parse',
                                       '--show-toplevel'], stderr=subprocess.DEVNULL)
        return root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Must be running inside git repository!")


def execute_sql_file(conn, filepath):
    with open(filepath, 'r') as f:
        sql = f.read()
    with conn.cursor() as cur:
        cur.execute(sql)
        # Print any notices PostgreSQL sent during execution
        if conn.notices:
            print("PostgreSQL notices:")
            for notice in conn.notices:
                print(notice.strip())
            # Clear notices after printing so they don't repeat
            conn.notices.clear()
    conn.commit()
    print(f"{filepath} executed.")


def main():


    db_path = os.path.join(get_root(), 'db')

    # Connect to new DB as admin
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "swiss_tournament"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432")
        )
        print("Connection to the database was successful.")
    except Exception as err:
        print(f"Failed to connect to the database: {err}")
        exit(1)

    try:
        execute_sql_file(conn, os.path.join(db_path, 'schema_permissions.sql'))
        execute_sql_file(conn, os.path.join(db_path, 'tables.sql'))
        execute_sql_file(conn, os.path.join(db_path, 'table_permissions.sql'))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
