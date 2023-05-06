#!/usr/bin/env python3

import psycopg2
import subprocess
import os
from pathlib import Path


def current_dir():
    return Path(__file__).resolve().parent

# Connect to the PostgreSQL database
# conn = psycopg2.connect(
#     host="localhost",
#     user="postgres",
#     password="postgres"
# )

conn_string = "postgresql://postgres:postgres@localhost"

dbname = "tournament"

# Open a cursor to perform database operations
conn = psycopg2.connect(conn_string)

# Set the isolation level to autocommit
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

# Create the database if it doesn't exist
cur = conn.cursor()

cur.execute(f"SELECT datname FROM pg_database WHERE datname='{dbname}'")

dbExists = cur.fetchone()

if dbExists:
    print(f"Database {dbname} already exists")
else:
    cur.execute(f"CREATE DATABASE {dbname}")
    print(f"Database {dbname} created")

# Execute a SELECT statement to retrieve tables from database
cur.execute(f"SELECT table_name "
            "FROM information_schema.tables "
            "WHERE table_schema = 'public'")
table_names = cur.fetchall()
print([table_name[0] for table_name in table_names])

# Create tables
# cmd = ['python3',
#        os.path.join(current_dir(), 'create-tables.py'),
#        '--conn', conn_string]

# try:
#     subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
# except subprocess.CalledProcessError as e:
#     print("Error details:", e.stderr)

# Register players
cmd = ['python3',
       os.path.join(current_dir(), 'register-players.py'),
       '--conn', conn_string]

try:
    subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
except subprocess.CalledProcessError as e:
    print("Error details:", e.stderr)

# Close the cursor and database connection
cur.close()
conn.close()
