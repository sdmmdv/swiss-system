#!/usr/bin/env python3

import csv
import psycopg2
from pathlib import Path
import argparse
import subprocess
import os

def root_dir():
    try:
        root = subprocess.check_output(['git', 'rev-parse',
                                       '--show-toplevel'], stderr=subprocess.DEVNULL)
        return root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Must be running inside git repository!")

def register_players(conn, csv_file):
    try:
        with conn.cursor() as cur:
            with open(csv_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)

                for row in reader:
                    cur.execute("""
                        INSERT INTO players (id, name, email) 
                        VALUES (%s, %s, %s)
                    """, (row['id'], row['name'], row['email']))

        conn.commit()
        print("All players registered successfully.")
    except Exception as err:
        conn.rollback()
        print("An unexpected error occurred. Rolled back all changes.")
        print(f"Reason: {err}")

if __name__ == '__main__':
    dbname=os.getenv("DB_NAME")
    user=os.getenv("DB_USER")
    password=os.getenv("DB_PASS")
    host=os.getenv("DB_HOST", "localhost")
    port=os.getenv("DB_PORT", "5432")
    
    required_vars = [dbname, user, password, host, port]
    if not all(required_vars):
        raise ValueError("One or more required environment variables are missing.")

    conn_string = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
    
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn',
                        help='PostgreSQL connection string',
                        default=conn_string)
    parser.add_argument('--csv-file',
                        help='CSV file containing player data',
                        default=os.path.join(root_dir(), 'data/players.csv'))
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    # Register players from CSV file
    register_players(conn, args.csv_file)

    # Close database connection
    conn.close()