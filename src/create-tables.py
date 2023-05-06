#!/usr/bin/env python3

import psycopg2
import argparse

# Function to create the Players table

def create_players_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Players (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()
        print("Players table created successfully")

# Function to create the Results table
def create_results_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Results (
                id SERIAL PRIMARY KEY,
                player1_id INTEGER REFERENCES Players(id) NOT NULL,
                player2_id INTEGER REFERENCES Players(id),
                date_time TIMESTAMP NOT NULL,
                player1_score INTEGER,
                player2_score INTEGER,
                CONSTRAINT one_result_per_player CHECK (player1_id != player2_id)
            )
        """)
        conn.commit()
        print("Results table created successfully")

# Function to create the Standings table
def create_standings_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Standings (
                player_id INTEGER REFERENCES Players(id),
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                PRIMARY KEY (player_id)
            )
        """)
        conn.commit()
        print("Standings table created successfully")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', help='Database connection string', required=True)
    args = parser.parse_args()
    conn = psycopg2.connect(args.conn)

    # Create the tables
    create_players_table(conn)
    create_results_table(conn)
    create_standings_table(conn)

if __name__ == '__main__':
    main()
