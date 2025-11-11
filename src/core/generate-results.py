#!/usr/bin/env python3

import csv
import random
from pathlib import Path
import subprocess

from common.db_utils import get_connection_string

from common.common import root_dir

def read_players(file_path):
    players = []
    with open(file_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            player_id, player_name, player_email = row
            player = {'id': player_id, 'name': player_name, 'email': player_email}
            players.append(player)
    return players

def generate_pairings(players):
    num_players = len(players)
    if num_players % 2 == 1:
        # If there are an odd number of players, add a dummy player
        players.append({'id': 'dummy', 'name': 'Dummy Player', 'email': ''})
        num_players += 1
    random.shuffle(players)
    pairings = []
    for i in range(num_players // 2):
        player1 = players[i*2]
        player2 = players[i*2+1]
        pairings.append({
            'player1_id': player1['id'],
            'player1_name': player1['name'],
            'player2_id': player2['id'],
            'player2_name': player2['name']
        })
    return pairings

def write_results(file_path, pairings, round_num):
    with open(file_path, 'w', newline='') as csvfile:
        fieldnames = ['round', 'player1_id', 'player1_name', 'player1_score', 'player2_score', 'player2_name', 'player2_id']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if csvfile.tell() == 0:
            writer.writeheader()
        for pairing in pairings:
            writer.writerow({
                'round': round_num,
                'player1_id': pairing['player1_id'],
                'player1_name': pairing['player1_name'],
                'player1_score': 0,
                'player2_score': 0,
                'player2_name': pairing['player2_name'],
                'player2_id': pairing['player2_id']
            })
def main():
    players_path = root_dir(__file__) / 'data/players.csv'

    # Read players from players.csv
    players = read_players(players_path)

    # Generate pairings
    pairings = generate_pairings(players)

    # Write pairings to results.csv for round 1
    results_path = root_dir(__file__) / 'data/results.csv'

    write_results(results_path, pairings, 1)

if __name__ == '__main__':
    main()