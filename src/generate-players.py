#!/usr/bin/env python3

import csv
from faker import Faker
from pathlib import Path
import subprocess
import os

fake = Faker()


def root_dir():
    try:
        root = subprocess.check_output(['git', 'rev-parse',
                                       '--show-toplevel'], stderr=subprocess.DEVNULL)
        return root.decode('utf-8').strip()
    except subprocess.CalledProcessError:
        raise RuntimeError("Must be running inside git repository!")

def main():
    # Generate 100 player records
    players = []
    for i in range(100):
        player_id = fake.numerify(text='#####')
        name = fake.name()
        email = fake.email()
        players.append((player_id, name, email))

    # Write players to CSV file
    with open(os.path.join(root_dir(), 'data/players.csv'), 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'email'])
        writer.writerows(players)

if __name__ == '__main__':
    main()
