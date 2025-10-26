#!/usr/bin/env python3

import psycopg2
import argparse
from pathlib import Path
import csv
import subprocess
import os
import math

from player import Player
from common.db_utils import get_connection_string
from common.logger import get_logger

logger = get_logger(__name__)

# Get eligible list of players in order of rankings to pair for the next round
def get_active_players(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, name, is_bye
            FROM Standings
            WHERE is_active = true
            ORDER BY points DESC, tiebreaker_A DESC, tiebreaker_B DESC, tiebreaker_C DESC;
        """)
        player_data = cur.fetchall()
    players = [Player(rank + 1, *data) for rank, data in enumerate(player_data)]
    return players

def validate_new_round(conn, tourney_type, max_round_count, round_id: int):
    """
    Validate that the given round_id is valid:
    - Cannot be less than maximum set by tournament type.
    - Cannot be less than max round already in results.
    - Must be exactly +1 greater than the current max round.
    """
    if max_round_count == 0:
        raise ValueError(
            f"No players are registered in the standings table. "
            f"Cannot start or validate round {round_id} for {tourney_type} tournament."
        )

    if round_id > max_round_count:
        raise ValueError(
            f"Invalid round {round_id}! {tourney_type} tournament is limited to maximum {max_round_count} rounds ."
        )
 
    with conn.cursor() as cur:
        cur.execute("SELECT COALESCE(MAX(round_id), 0) FROM results;")
        max_round_id = cur.fetchone()[0]

    if round_id <= max_round_id:
        raise ValueError(
            f"Invalid round {round_id}: must be greater than last applied round {max_round_id}."
        )

    if round_id != max_round_id + 1:
        raise ValueError(
            f"Invalid round {round_id}: Last round was {max_round_id}, next round must be {max_round_id + 1}!"
        )

    logger.info(f"Round {round_id} is valid (previous max round = {max_round_id})")
    return True


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
    """
    Generate Swiss-style tournament pairings.

    The Swiss pairing algorithm:
    1. Avoids pairing players who have already played each other.
    2. Pairs players close in ranking order.
    3. Handles BYE players first (those resting or absent).
    4. Tries to fix conflicts by swapping opponents if necessary.
    5. Assigns a 'BYE' if no valid opponent is available.

    Args:
        conn: Database connection (used for head-to-head history).
        players (list): List of player objects with attributes:
                        - id
                        - name
                        - is_bye (bool)

    Returns:
        list of tuples: Each tuple contains (playerA, playerB) or (player, 'BYE').

    Algorithm Complexity:
        Time Complexity:
            O(n²) —
                The algorithm may compare each player with all others
                to ensure no repeated matchups, and can backtrack or
                swap pairings in conflict cases. This quadratic growth
                is typical for Swiss pairing algorithms of moderate player counts.

        Space Complexity:
            O(n + m) —
                - O(n) for tracking paired players and pairings.
                - O(m) for the head-to-head map (where m is the number of past matches).
                Total space remains linear with respect to the number of players
                and previously recorded results.
    """
    head_to_head_map = create_head_to_head_map(conn)
    paired_players = set()
    pairings = []

    # Handle BYE players (rested players) firs
    for i in range(len(players) - 1, -1, -1):
        player = players[i]
        if player.is_bye and player.id not in paired_players:
            left_player = player
            paired_players.add(player.id)

            # Try to pair BYE player with someone above in rankings
            for j in range(i - 1, -1, -1):
                opponent = players[j]
                if not opponent.is_bye and opponent.id not in paired_players and \
                   not have_played_before(head_to_head_map, left_player.id, opponent.id):
                    pairings.append((left_player, opponent))
                    paired_players.add(opponent.id)
                    logger.debug(f"{left_player.id} {left_player.name} - {opponent.name} {opponent.id}")
                    break
            else:
                # No valid opponent found upwards, try downwards
                for j in range(i, len(players)):
                    opponent = players[j]
                    if not opponent.is_bye and opponent.id not in paired_players and \
                       not have_played_before(head_to_head_map, left_player.id, opponent.id):
                        pairings.append((left_player, opponent))
                        paired_players.add(opponent.id)
                        logger.debug(f"{left_player.id} {left_player.name} - {opponent.name} {opponent.id}")
                        break

    # Pair remaining active players from top to bottom
    for i, left_player in enumerate(players):
        if left_player.id in paired_players:
            continue

        paired_players.add(left_player.id)

        for j, right_player in enumerate(players[i:], start=i):
            if right_player.id in paired_players:
                continue

            # Case: They haven't played before — simple pairing
            if not have_played_before(head_to_head_map, left_player.id, right_player.id):
                pairings.append((left_player, right_player))
                paired_players.add(right_player.id)
                logger.debug(f"{left_player.id} {left_player.name} - {right_player.name} {right_player.id}")
                break

            # Case: All possible opponents already played — try reshuffling
            if j == len(players) - 1:
                for k in range(len(pairings) - 1, -1, -1):
                    player1, player2 = pairings[k]
                    id1, id2 = player1.id, player2.id

                    # Try swapping with pair (player1, player2)
                    if not have_played_before(head_to_head_map, left_player.id, id2) and \
                    not have_played_before(head_to_head_map, id1, right_player.id):
                        pairings[k] = (player1, right_player)
                        pairings.append((left_player, player2))
                        paired_players.add(right_player.id)
                        logger.debug(f"Swap pairing: {id1}-{right_player.id}, {left_player.id}-{player2.id}")
                        break

                    elif not have_played_before(head_to_head_map, left_player.id, id1) and \
                        not have_played_before(head_to_head_map, right_player.id, id2):
                        pairings[k] = (player1, left_player)
                        pairings.append((right_player, player2))
                        paired_players.add(right_player.id)
                        logger.debug(f"Swap pairing: {id1}-{left_player.id}, {right_player.id}-{player2.id}")
                        break

    return pairings

def root_dir():
    try:
        root = subprocess.check_output(['git', 'rev-parse',
                                       '--show-toplevel'], stderr=subprocess.DEVNULL)
        return root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Must be running inside git repository!")

def generate_pairings_csv(sorted_pairs, round_id):
    filename = os.path.join(root_dir(), 'data', f'pairings_r{round_id}.csv')
    filename_display = os.path.join(root_dir(), 'data', 'pairings-display.txt')

    os.makedirs(os.path.dirname(filename), exist_ok=True)  # ensure data/ dir exists

    with open(filename, 'w', newline='') as file, open(filename_display, 'w') as f:
        writer = csv.writer(file)
        writer.writerow(["round_id", "player1_id", "player1_name", "player1_score", "player2_score", "player2_name", "player2_id"])

        for pair in sorted_pairs:
            player1 = pair[0]
            player2 = pair[1]

            if player2 == "BYE":
                row = [round_id, player1.id, player1.name, "BYE", "_", "_", "_"]
                row_display = f"{player1.name} has a BYE\n"
            else:
                row = [round_id, player1.id, player1.name, "?", "?", player2.name, player2.id]
                row_display = f'{player1.name} ?  -  ? {player2.name}\n'

            writer.writerow(row)
            f.write(row_display)

    logger.info(f"Pairings CSV file generated successfully: {filename}")

def get_player_count(conn) -> int:
    """
    Count the number of players in the standings table.
    """
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(id) FROM standings;")
        num_players = cur.fetchone()[0] or 0
    return num_players


def get_max_rounds(num_players: int, system: str = "swiss") -> int:
    """
    Calculate maximum number of rounds for a tournament.
    
    system = "swiss"  → ceil(log2(N))
    system = "roundrobin" → N - 1
    """
    if num_players < 2:
        return 0

    if system == "roundrobin":
        return num_players - 1
    elif system == "swiss":
        return math.ceil(math.log2(num_players))
    else:
        raise ValueError("Unknown system: choose 'swiss' or 'roundrobin'")


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
    parser.add_argument("-t", "--type",
                        type=str,
                        choices=["roundrobin", "swiss"],
                        default="roundrobin",
                        help="Tournament type (default: roundrobin)"
    )
    args = parser.parse_args()

    # Connect to the database
    conn = psycopg2.connect(args.conn)

    player_count = get_player_count(conn)

    max_rounds = get_max_rounds(player_count, args.type)

    validate_new_round(conn, args.type, max_rounds, args.round_id)

    active_players = get_active_players(conn)
    # [print(player) for player in active_players]

    raw_pairs = swiss_pairing(conn, active_players)

    # Sort the raw_pairs list by the rank of the first element in each pair
    sorted_pairs = sorted(raw_pairs, key=lambda pair: pair[0].rank)

    # [print(f'{pair[0]} - {pair[1]}') for pair in raw_pairs]

    generate_pairings_csv(sorted_pairs, args.round_id)

    # Close database connection
    conn.close()