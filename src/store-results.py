#!/usr/bin/env python3

from pathlib import Path
import argparse
import psycopg2
import csv
import os
import sys

def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent

def store_results(input_file, conn):
    cur = None
    try:
        cur = conn.cursor()
        with open(input_file, mode='r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                round_id = int(row['round_id'])
                player1_id = row['player1_id']
                player1_name = row['player1_name']
                player1_score = row['player1_score']
                player2_score = row['player2_score']
                player2_name = row['player2_name']
                player2_id = row['player2_id']
                

                if player1_score == 'BYE':
                    player1_score = 2.0
                    player2_score, player2_name, player2_id = '0.0', '_', '_'
                else:
                    row_output = ','.join([str(round_id), player1_id, player1_name, player1_score, player2_score, player2_name, player2_id])
                    try:
                        player1_score = float(player1_score)
                        if player1_score not in [0.5, 0.0, 1.0, 1.5, 2.0]:
                            raise ValueError('Invalid player1_score')
                    except ValueError:
                        print(f'Invalid player2_score: {player1_score}\n{row_output}')                       
                        conn.rollback()
                        sys.exit(1)

                    try:
                        player2_score = float(player2_score)
                        if player2_score not in [0.5, 0.0, 1.0, 1.5, 2.0]:
                            raise ValueError('Invalid player2_score')
                    except ValueError:
                        print(f'Invalid player2_score: {player2_score}\n{row_output}')
                        conn.rollback()
                        sys.exit(1)

                    # try:
                    #     if player1_score + player2_score != 2.0:
                    #         msg = 'Sum of player scores must be 2.0'
                    #         raise ValueError(msg)
                    # except ValueError:
                    #     print(f'Invalid sum of players! {msg}\n{row_output}')
                    #     conn.rollback()
                    #     sys.exit(1)

                cur.execute("INSERT INTO results (round_id, player1_id, player1_name, player1_score, player2_score, player2_name, player2_id) "
                            "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                            (round_id, player1_id, player1_name, player1_score, player2_score, player2_name, player2_id))

        print("Results stored successfully.")
        conn.commit()
    except (psycopg2.Error, FileNotFoundError) as e:
        if conn is not None:
            conn.rollback()
        print(f"Error: {str(e)}")
    finally:
        if cur is not None:
            cur.close()


def main():
    conn_string = "postgresql://postgres:postgres@localhost"

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', 
                        help='PostgreSQL connection string',
                        default=conn_string)
    parser.add_argument('-f',
                        '--input-file',
                        default=root_dir() / 'data/results.csv',
                        help=f'Results csv input file (default: %(default)s)')
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)


    store_results(args.input_file, conn)

    # Close database connection
    conn.close()

if __name__ == '__main__':
    main()