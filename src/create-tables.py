#!/usr/bin/env python3

import psycopg2
import argparse

# Function to create the Players table

def create_players_table(conn):
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS Players (
                id VARCHAR(25) PRIMARY KEY,
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
                round_id INTEGER PRIMARY KEY NOT NULL,
                player1_id VARCHAR(25) REFERENCES Players(id) NOT NULL,
                player1_name VARCHAR(255) NOT NULL,
                player1_score DECIMAL(2,1) NOT NULL,
                player2_score DECIMAL(2,1),
                player2_name VARCHAR(255),
                player2_id VARCHAR(25) REFERENCES Players(id),
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
                id VARCHAR(25) REFERENCES Players(id),
                name VARCHAR(255),
                is_active BOOLEAN,
                is_bye BOOLEAN,
                tiebreaker_C DECIMAL(4,2),
                tiebreaker_B DECIMAL(4,2),
                tiebreaker_A DECIMAL(4,2),
                points DECIMAL(2,1),
                PRIMARY KEY (id)
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
