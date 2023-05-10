#!/usr/bin/env python3

import psycopg2
import argparse

# Get eligible list of players to pair for the next round
def get_active_players(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT rank, id, name, is_bye FROM standings WHERE is_active = true ORDER BY rank DESC")
        players = cur.fetchall()
    return players

def swiss_pairing(conn, players):
    paired_players = []

    # Pair already rested players from the bottom going upwards
    for i in range(len(players) - 1, -1, -1):
        rank, player_id, name, is_bye = players[i]
        
        if is_bye and player_id not in paired_players:
            left_hand_player = player_id
            paired_players.append(left_hand_player)
            
            for j in range(i - 1, -1, -1):
                rank, opponent_id, opponent_name, is_opponent_bye = players[j]
                
                if not is_opponent_bye and opponent_id not in paired_players:
                    right_hand_player = opponent_id
                    paired_players.append(right_hand_player)
                    print(f"{left_hand_player} {name} - {opponent_name} {right_hand_player}")
                    break

            # If no player found, pair going downwards the table
            else:
                for j in range(i, len(players)):
                    rank, opponent_id, opp_name, is_opponent_bye, _ = players[j]
                    
                    if not is_opponent_bye and opponent_id not in paired_players:
                        right_hand_player = opponent_id
                        paired_players.append(right_hand_player)
                        print(f"{left_hand_player} {name} - {opp_name} {right_hand_player}")
                        break

    # Pair leading players from up to bottom (by ranking)
    for i in range(len(players)):
        rank, player_id, name, is_bye = players[i]

        if player_id not in paired_players:
            left_hand_player = player_id
            paired_players.append(left_hand_player)

            for j in range(i, len(players)):
                rank, opponent_id, opp_name, is_opponent_bye = players[j]

                if opponent_id not in paired_players:
                    right_hand_player = opponent_id
                    paired_players.append(right_hand_player)
                    print(f"{left_hand_player} {name} - {opp_name} {right_hand_player}")
                    break
            else:
                print(f"{left_hand_player} {name} - BYE")
                break


if __name__ == '__main__':
    conn_string = "postgresql://postgres:postgres@localhost"

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--conn', 
                        help='PostgreSQL connection string',
                        default=conn_string)
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    
    active_players = get_active_players(conn)
    print(active_players)

    pairs = swiss_pairing(conn, active_players)

    # Close database connection
    conn.close()