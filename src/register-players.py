#!/usr/bin/env python3

import csv
import psycopg2
from pathlib import Path
import argparse

def current_dir():
    return Path(__file__).resolve().parent


def register_players(conn):
    # Open CSV file for reading
    with open(current_dir() / 'data' / 'players.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Connect to the database
        with conn.cursor() as cur:
            # Loop over each row in the CSV file
            for row in reader:
                # Insert row into database
                cur.execute("INSERT INTO player (id, name, email) VALUES (%s, %s, %s)",
                            (row['id'], row['name'], row['email']))

        # Commit changes to the database
        conn.commit()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', help='PostgreSQL connection string')
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    # Register players from CSV file
    register_players(conn)

    # Close database connection
    conn.close()