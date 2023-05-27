#!/usr/bin/env python3

import psycopg2
import argparse
import sys

def apply_scores_to_standings(conn, round_id):
    try:
        with conn.cursor() as cur:
            # Fetch all the results from the results table
            cur.execute("SELECT * FROM results WHERE round_id = %s", (round_id,))
            results = cur.fetchall()
            if not results:
                raise ValueError(f"Round ID {round_id} does not exist in the table")

            # Apply the scores to the standings table
            for result in results:
                round_id = result[0]
                player1_id = result[1]
                player1_score = result[3]
                player2_score = result[4]
                player2_id = result[6]


                # Update player1's score in standings table
                cur.execute("UPDATE standings SET points = points + %s WHERE id = %s", (player1_score, player1_id))

                # Check if player2_name and player2_id are empty
                if player2_id != '_':
                    # Update player2's score in standings table
                    cur.execute("UPDATE standings SET points = points + %s WHERE id = %s", (player2_score, player2_id))

            # Commit the changes to the database
            conn.commit()
            print("Record applied successfully")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        sys.exit(1)


def update_standings_table(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT *
                FROM Standings
                ORDER BY points DESC, tiebreaker_A DESC, tiebreaker_B DESC, tiebreaker_C DESC;
            """)
            rows = cur.fetchall()
            
            # Update the ordering in the fetched rows
            for new_rank, row in enumerate(rows, start=1):
                cur.execute("""
                    UPDATE Standings
                    SET points = %s, tiebreaker_A = %s, tiebreaker_B = %s, tiebreaker_C = %s
                    WHERE id = %s;
                """, (row[7], row[6], row[5], row[4], row[0]))
            
            conn.commit()
            print("Standings table updated successfully")
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        sys.exit(1)


def print_standings(conn):
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT
                    ROW_NUMBER() OVER (ORDER BY points DESC) AS rank,
                    id,
                    name,
                    is_active,
                    is_bye,
                    tiebreaker_c,
                    tiebreaker_b,
                    tiebreaker_a,
                    points
                FROM
                    standings;
            """)

            rows = cur.fetchall()

            # Print the column names
            print("Rank | ID          | Name                 | Active | Bye  | Tiebreaker C | Tiebreaker B | Tiebreaker A | Points")
            print("-----+-------------+----------------------+--------+------+--------------+--------------+--------------+-------")

            # Iterate over the results and print each row
            for row in rows:
                formatted_row = "{:<4} | {:<11} | {:<20} | {:<6} | {:<4} | {:<12} | {:<12} | {:<12} | {:<6}".format(*row)
                print(formatted_row)

    except psycopg2.Error as e:
        print(f"Error: {str(e)}")

if __name__ == '__main__':
    conn_string = "postgresql://postgres:postgres@localhost"

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', 
                        help='PostgreSQL connection string',
                        default=conn_string)
    parser.add_argument("-r",
                        "--round-id",
                        type=int,
                        required=True,
                        help="Round ID")
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    # Apply scores to standings
    # apply_scores_to_standings(conn, args.round_id)

    # Update standings table
    update_standings_table(conn)

    # Print the standings
    print_standings(conn)



    # Close database connection
    conn.close()