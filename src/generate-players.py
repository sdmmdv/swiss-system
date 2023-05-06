#!/usr/bin/env python3

import csv
from faker import Faker
from pathlib import Path

fake = Faker()


def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent

def main():
    # Generate 100 player records
    players = []
    for i in range(100):
        player_id = fake.numerify(text='#####')
        name = fake.name()
        email = fake.email()
        players.append((player_id, name, email))

    # Write players to CSV file
    with open(root_dir() / 'data/players.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['id', 'name', 'email'])
        writer.writerows(players)

if __name__ == '__main__':
    main()
