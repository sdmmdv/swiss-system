#!/usr/bin/env python3

import csv
from faker import Faker
from pathlib import Path
import subprocess
import os

from common.logger import get_logger

logger = get_logger(__name__)

fake = Faker()


def root_dir():
    try:
        root = subprocess.check_output(['git', 'rev-parse',
                                       '--show-toplevel'], stderr=subprocess.DEVNULL)
        return root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Must be running inside git repository!")


def main():
    players = []
    used_ids = set()

    while len(players) < 100:
        player_id = fake.numerify(text='#####')
        if player_id in used_ids:
            continue  # skip duplicates
        used_ids.add(player_id)

        name = fake.name()
        email = fake.email()
        players.append((player_id, name, email))

    # Ensure target dir exists
    data_dir = Path(root_dir()) / 'data'
    data_dir.mkdir(parents=True, exist_ok=True)

    # Write players to CSV file
    with open(data_dir / 'players.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'email'])
        writer.writerows(players)


if __name__ == '__main__':
    main()
