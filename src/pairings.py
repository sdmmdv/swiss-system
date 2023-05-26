#!/usr/bin/env python3

import psycopg2
import argparse

from player import Player

# Get eligible list of players to pair for the next round
def get_active_players(conn):
    with conn.cursor() as cur:
        cur.execute("SELECT rank, id, name, is_bye FROM standings WHERE is_active = true ORDER BY rank ASC")
        player_data = cur.fetchall()
    players = [Player(*data) for data in player_data]
    return players

# Given a player, get set of already played opponents
# useful function, but calling it every time will drain time resources
def fetch_played_opponents(conn, player_id):
    opponents = set()

    with conn.cursor() as cur:
        cur.execute("""
            SELECT player1_id, player2_id
            FROM results
            WHERE player1_id = %s OR player2_id = %s
        """, (player_id, player_id))

        for row in cur.fetchall():
            opponent1_id, opponent2_id = row

            if opponent1_id and opponent1_id != player_id:
                opponents.add(opponent1_id)

            if opponent2_id and opponent2_id != player_id:
                opponents.add(opponent2_id)

    return opponents

def create_head_to_head_map(conn):
    map_of_opponents = {}

    with conn.cursor() as cur:
        cur.execute("""
            SELECT player1_id, player2_id
            FROM results
        """)

        for row in cur.fetchall():
            opponent1_id, opponent2_id = row

            if opponent1_id:
                if opponent1_id not in map_of_opponents:
                    map_of_opponents[opponent1_id] = set()
                map_of_opponents[opponent1_id].add(opponent2_id)

            if opponent2_id:
                if opponent2_id not in map_of_opponents:
                    map_of_opponents[opponent2_id] = set()
                map_of_opponents[opponent2_id].add(opponent1_id)

    return map_of_opponents

# Set a verdict if player1 has played against player2
def have_played_before(head_to_head_map, player1_id, player2_id):
    return player1_id in head_to_head_map and player2_id in head_to_head_map[player1_id]


def swiss_pairing(conn, players):
    paired_players_set = set()
    pairing_list = [] 

    H2H_map = create_head_to_head_map(conn)

    # Pair already rested players from the bottom going upwards
    for i in range(len(players) - 1, -1, -1):
        rank = players[i].rank
        player_id = players[i].id
        name = players[i].name
        is_bye = players[i].is_bye
        
        if is_bye and player_id not in paired_players_set:
            left_hand_player = player_id
            paired_players_set.add(left_hand_player)
            
            for j in range(i - 1, -1, -1):
                opponent_id = players[j].id
                opponent_name = players[j].name
                is_opponent_bye = players[j].is_bye
                
                if not is_opponent_bye and opponent_id not in paired_players_set and \
                    not have_played_before(H2H_map, left_hand_player, opponent_id):
                    right_hand_player = opponent_id
                    paired_players_set.add(right_hand_player)
                    pairing_list.append((players[i], players[j]))
                    # print(f"{left_hand_player} {name} - {opponent_name} {right_hand_player}")
                    break

            # If no player found, pair going downwards the table
            else:
                for j in range(i, len(players)):
                    opponent_id = players[j].id
                    opp_name = players[j].name
                    is_opponent_bye = players[j].is_bye
                    
                    if not is_opponent_bye and opponent_id not in paired_players_set and \
                        not have_played_before(H2H_map, left_hand_player, opponent_id):
                        right_hand_player = opponent_id
                        paired_players_set.add(right_hand_player)
                        pairing_list.append((players[i], players[j]))
                        # print(f"{left_hand_player} {name} - {opp_name} {right_hand_player}")
                        break

    # Pair leading players from up to bottom (by ranking)
    for i in range(len(players)):
        player_id = players[i].id
        name = players[i].name
        is_bye = players[i].is_bye

        if player_id not in paired_players_set:
            left_hand_player = player_id
            paired_players_set.add(left_hand_player)

            for j in range(i, len(players)):
                opponent_id = players[j].id
                opp_name = players[j].name
                is_opponent_bye = players[j].is_bye

                if opponent_id not in paired_players_set:

                    right_hand_player = opponent_id

                    if not have_played_before(H2H_map, left_hand_player, right_hand_player):
                        paired_players_set.add(right_hand_player)
                        pairing_list.append((players[i], players[j]))
                        # print(f"{left_hand_player} {name} - {opp_name} {right_hand_player}")
                        break

                    # If about to match players matched before
                    # Iterate over the list(from end to front of list)
                    # From matched players seek for a player which not faced left_hand_player
                    # switch mutual opponents of players if they haven't played before.
                    else:

                        for ind in range(len(pairing_list) - 1, -1, -1):
                            # id1, id2 = pairing_list[ind]
                            player1, player2 = pairing_list[ind]
                            id1, id2 = player1.id, player2.id
                            
                            if not have_played_before(H2H_map, left_hand_player, id2) and \
                                not have_played_before(H2H_map, id1, right_hand_player):
                                pairing_list[ind] = (player1, players[j])
                                # print(f"change {id1} - {right_hand_player}")
                                pairing_list.append((players[i], player2))
                                paired_players_set.add(right_hand_player)
                                break
                            
                            elif not have_played_before(H2H_map, left_hand_player, id1) and \
                                not have_played_before(H2H_map, right_hand_player, id2):
                                pairing_list[ind] = (player1, players[i])
                                # print(f"change {id1} - {left_hand_player}")
                                pairing_list.append((players[j], player2))
                                paired_players_set.add(right_hand_player)
                                break                     


            else:
                # print(f"{left_hand_player} {name} - BYE")
                pairing_list.append((players[i], 'BYE'))
                break

    return pairing_list

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
    # [print(player) for player in active_players]

    pairs = swiss_pairing(conn, active_players)
    [print(f'{pair[0]} - {pair[1]}') for pair in pairs]

    # Close database connection
    conn.close()