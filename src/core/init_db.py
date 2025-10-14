#!/usr/bin/env python3

import os
import psycopg2
import subprocess

from common.db_utils import get_connection_string
from common.logger import get_logger

logger = get_logger(__name__)

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
            logger.info("PostgreSQL notices:")
            for notice in conn.notices:
                logger.info(notice.strip())
            # Clear notices after printing so they don't repeat
            conn.notices.clear()
    conn.commit()
    logger.info(f"{filepath} executed.")


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
        logger.info("Connection to the database was successful.")
    except Exception as err:
        logger.error(f"Failed to connect to the database: {err}")
        exit(1)

    try:
        execute_sql_file(conn, os.path.join(db_path, 'schema_permissions.sql'))
        execute_sql_file(conn, os.path.join(db_path, 'tables.sql'))
        execute_sql_file(conn, os.path.join(db_path, 'table_permissions.sql'))
    finally:
        conn.close()

if __name__ == "__main__":
    main()
