#!/usr/bin/env python3

import psycopg2
import argparse

# Function to create the Player table

def create_player_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Player (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                email VARCHAR(255) NOT NULL
                -- Add any other fields you need
            )
        """)
        conn.commit()
        print("Player table created successfully")

# Function to create the Match table
def create_match_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Match (
                id SERIAL PRIMARY KEY,
                player1_id INTEGER REFERENCES Player(id) NOT NULL,
                player2_id INTEGER REFERENCES Player(id),
                date_time TIMESTAMP NOT NULL,
                player1_score INTEGER,
                player2_score INTEGER,
                CONSTRAINT one_match_per_player CHECK (player1_id != player2_id)
            )
        """)
        conn.commit()
        print("Match table created successfully")

# Function to create the Tournament_Standings table
def create_standings_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Tournament_Standings (
                player_id INTEGER REFERENCES Player(id),
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                draws INTEGER DEFAULT 0,
                PRIMARY KEY (player_id)
            )
        """)
        conn.commit()
        print("Tournament_Standings table created successfully")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', help='Database connection string', required=True)
    args = parser.parse_args()
    conn = psycopg2.connect(args.conn)

    # Create the tables
    create_player_table(conn)
    create_match_table(conn)
    create_standings_table(conn)

if __name__ == '__main__':
    main()
