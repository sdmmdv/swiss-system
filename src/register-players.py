#!/usr/bin/env python3

import csv
import psycopg2
from pathlib import Path
import argparse

def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent

def register_players(conn, csv_file):
    # Open CSV file for reading
    with open(csv_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Connect to the database
        with conn.cursor() as cur:
            # Loop over each row in the CSV file
            for row in reader:
                # Insert row into database
                cur.execute("INSERT INTO players (id, name, email) VALUES (%s, %s, %s)",
                            (row['id'], row['name'], row['email']))

        # Commit changes to the database
        conn.commit()

if __name__ == '__main__':
    conn_string = "postgresql://postgres:postgres@localhost"

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', 
                        help='PostgreSQL connection string',
                        default=conn_string)
    parser.add_argument('--csv-file',
                        help='CSV file containing player data',
                        default=root_dir() / 'data/players.csv')
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    # Register players from CSV file
    register_players(conn, args.csv_file)

    # Close database connection
    conn.close()