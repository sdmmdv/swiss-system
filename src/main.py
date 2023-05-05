#!/usr/bin/env python3

import psycopg2

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    user="postgres",
    password="postgres"
)

dbname = "tournament"

# Open a cursor to perform database operations
cur = conn.cursor()

# Set the isolation level to autocommit
conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)

# Create the database if it doesn't exist
cur = conn.cursor()
cur.execute(f'DROP DATABASE IF EXISTS {dbname}')
cur.execute(f'CREATE DATABASE {dbname}')

# Execute a SELECT statement to retrieve tables from database
cur.execute('select * from information_schema.tables')

# Close the cursor and database connection
cur.close()
conn.close()
