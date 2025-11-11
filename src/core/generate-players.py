#!/usr/bin/env python3

import csv
from faker import Faker
from pathlib import Path
import subprocess
import os
import argparse

from common.logger import get_logger
from common.common import root_dir

logger = get_logger(__name__)

fake = Faker()

def generate_fake_players(num_players):
    """
    Generate a list of fake players with unique IDs, names, and emails.

    Args:
        num_players (int): Number of players to generate.

    Returns:
        list[tuple]: List of tuples (id, name, email)
    """
    players = []
    used_ids = set()

    logger.debug(f"Starting generation of {num_players} players...")
    while len(players) < num_players:
        player_id = fake.numerify(text='#####')
        if player_id in used_ids:
            continue  # skip duplicates
        used_ids.add(player_id)

        name = fake.name()
        email = fake.email()
        players.append((player_id, name, email))

    logger.debug(f"Generated {len(players)} players successfully.")
    return players


def write_players_to_csv(players, output_path):
    """
    Write the list of players to a CSV file.

    Args:
        players (list[tuple]): List of player tuples.
        output_path (Path): Destination CSV file path.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'email'])
        writer.writerows(players)

    logger.info(f"Successfully wrote {len(players)} players to {output_path}")


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate tournament players using Faker."
    )
    parser.add_argument(
        '-n', '--num-players',
        type=int,
        default=10,
        help='Number of players to generate (default: 10)'
    )
    return parser.parse_args()


# ------------------------------------------------------------
# Main Entrypoint
# ------------------------------------------------------------
def main():
    args = parse_args()
    num_players = args.num_players

    logger.info(f"Generating {num_players} players...")

    players = generate_fake_players(num_players)

    data_dir = Path(root_dir(__file__)) / 'data'
    output_file = data_dir / 'players.csv'

    write_players_to_csv(players, output_file)


if __name__ == '__main__':
    main()
