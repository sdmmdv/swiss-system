#!/usr/bin/env python3

import psycopg2
import argparse
import sys
import os

from common.db_utils import get_connection_string

def apply_scores_to_standings(conn, round_id):
    try:
        with conn.cursor() as cur:
            # Fetch all the results from the results table
            cur.execute("SELECT * FROM results WHERE round_id = %s", (round_id,))
            results = cur.fetchall()
            if not results:
                raise ValueError(f"Round ID {round_id} does not exist in the table")

            #Make sure to not apply duplicate rounds
            cur.execute("SELECT MAX(matches) FROM standings;")
            max_matches = cur.fetchone()[0] or 0
            if not (round_id > max_matches):
                raise ValueError(f"Round {round_id} already applied (matches = {max_matches})")


            # Apply the scores to the standings table
            for result in results:
                round_id = result[0]
                player1_id = result[1]
                player1_score = result[3]
                player2_score = result[4]
                player2_id = result[6]

                # Update number of matches played
                cur.execute("UPDATE standings SET matches = matches + 1 WHERE id IN (%s, %s)", (player1_id, player2_id))

                # Update player1's score in standings table
                cur.execute("UPDATE standings SET points = points + %s WHERE id = %s", (player1_score, player1_id))

                # Check if player2_id are empty
                if player2_id != '_':
                    # Update player2's score in standings table
                    cur.execute("UPDATE standings SET points = points + %s WHERE id = %s", (player2_score, player2_id))
                else:
                    # Store is_bye to standings
                    cur.execute(f"UPDATE standings SET is_bye = 'true' WHERE id = '{player1_id}'")

            # Commit the changes to the database
            conn.commit()
            print("Record applied successfully")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        sys.exit(1)


def apply_buchholz_tiebreak(conn):
    try:
        # Retrieve the list of players from the standings table
        with conn.cursor() as cur:
            cur.execute("SELECT id, name FROM standings")
            players = cur.fetchall()
            # print(players)

            # Get average points of all players
            # cur.execute("SELECT AVG(points) AS average_points FROM standings")
            # result = cur.fetchone()
            # average_points = format(result[0], '.2f')

            # Update the Buchholz tie-breaker for each player
            for player in players:
                player_id = player[0]
                player_name = player[1]
                cur.execute("""
                    SELECT DISTINCT
                        CASE 
                            WHEN player1_id = %s THEN player2_id
                            WHEN player2_id = %s THEN player1_id
                        END AS opponent_id,
                        CASE
                            WHEN player1_id = %s THEN player2_score
                            WHEN player2_id = %s THEN player1_score
                        END AS opponent_score
                    FROM results
                    WHERE player1_id = %s OR player2_id = %s;
                """, ([player_id] * 6))

                # Fetch all the opponent results
                opponent_data = cur.fetchall()

                opponent_ids = [result[0] for result in opponent_data]
                # print(opponent_ids)

                cur.execute("""
                    SELECT COALESCE(SUM(points), 0) FROM standings WHERE id = ANY(%s);
                """, (opponent_ids,))

                buchholz_score_sum = cur.fetchone()[0]

                # print(player_id, player_name, opponent_data, buchholz_score_sum)

                # opponent_ids = [result[0] for result in opponent_data]
                # opponent_points = [result[1] for result in opponent_data]
                # buchholz_score_sum = sum(points for _, points in opponent_data)
                # print(player_id, player_name, opponent_data, buchholz_score_sum)

                try:
                    cur.execute("UPDATE standings SET tiebreaker_a = %s WHERE id = %s", (buchholz_score_sum, player_id))
                except psycopg2.Error as e:
                    conn.rollback()
                    print(f"Error: {str(e)}")
                    sys.exit(1)
            # Commit the changes to the database
            conn.commit()
            print("Buchholz applied successfully")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':    
    conn_string = get_connection_string()

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
    apply_scores_to_standings(conn, args.round_id)

    # Apply buchholz_tiebreak
    apply_buchholz_tiebreak(conn)


    # Close database connection
    conn.close()
