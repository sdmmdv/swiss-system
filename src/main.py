#!/usr/bin/env python3
"""
Swiss System Tournament Central CLI
-----------------------------------
This script acts as a unified command-line interface for managing
all tournament operations such as initializing the database,
registering players, generating pairings, updating standings,
and converting reports.
"""

import argparse
import subprocess
import sys
from pathlib import Path

# Path to the src directory containing all scripts
BASE_DIR = Path(__file__).resolve().parent

def run_script(script_name, *args):
    """Run one of the existing scripts via subprocess."""
    script_path = BASE_DIR / script_name
    cmd = [sys.executable, str(script_path)] + list(args)
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Swiss System Tournament Manager CLI"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. Initialize DB
    subparsers.add_parser("init-db", help="Initialize the tournament database")

    # 2. Generate players
    subparsers.add_parser("generate-players", help="Generate list of players")

    # 3. Register players
    subparsers.add_parser("register-players", help="Register players into the database")

    # 4. Generate pairings
    p = subparsers.add_parser("generate-pairings", help="Generate match pairings")
    p.add_argument("-r", "--round-id", required=True, help="Round ID")
    p.add_argument("-t", "--type", choices=["roundrobin", "swiss"], default="swiss", help="Pairing type")

    # 5. Register standings
    subparsers.add_parser("register-standings", help="Register tournament standings")

    # 6. Populate results
    p = subparsers.add_parser("populate-results", help="Populate results from a file")
    p.add_argument("-f", "--file", required=True, help="CSV file with results")

    # 7. Register results
    p = subparsers.add_parser("register-results", help="Register results into DB")
    p.add_argument("-f", "--input-file", required=True, help="Results input CSV file")
    p.add_argument("--conn", help="PostgreSQL connection string")

    # 8. Print table
    p = subparsers.add_parser("print-table", help="Print tournament tables")
    p.add_argument("-t", "--table", choices=["standings", "results", "players"], required=True)
    p.add_argument("--conn", help="PostgreSQL connection string")

    # 9. Apply results to standings
    p = subparsers.add_parser("apply-results", help="Apply results to standings for a given round")
    p.add_argument("-r", "--round-id", required=True)
    p.add_argument("--conn", help="PostgreSQL connection string")

    # 10. Convert Excel → CSV
    p = subparsers.add_parser("convert-excel-to-csv", help="Convert Excel file to CSV format")
    p.add_argument("--input", default="data/input.xlsx", help="Path to input Excel file")
    p.add_argument("--output", default="data/output.csv", help="Path to output CSV file")

    # 11. Convert table → Excel
    subparsers.add_parser("convert-table-to-excel", help="Convert DB tables to Excel format")

    # (Optional) Developer/test scripts
    test_parser = subparsers.add_parser("test", help="Run internal test scripts")
    test_parser.add_argument(
        "name",
        choices=["test_pairings", "test_player", "test_standings", "test_tournament"],
        help="Test script name (e.g., test_pairings)"
    )

    args, unknown = parser.parse_known_args()

    cmd = args.command

    try:
        if cmd == "init-db":
            run_script("init_db.py", *unknown)

        elif cmd == "generate-players":
            run_script("generate-players.py", *unknown)

        elif cmd == "register-players":
            run_script("register-players.py", *unknown)

        elif cmd == "generate-pairings":
            run_script("generate-pairings.py", "-r", args.round_id, "-t", args.type, *unknown)

        elif cmd == "register-standings":
            run_script("register-standings.py", *unknown)

        elif cmd == "populate-results":
            run_script("populate-results.py", "-f", args.file, *unknown)

        elif cmd == "register-results":
            cmd_args = ["-f", args.input_file]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("register-results.py", *cmd_args, *unknown)

        elif cmd == "print-table":
            cmd_args = ["-t", args.table]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("print-table.py", *cmd_args, *unknown)

        elif cmd == "apply-results":
            cmd_args = ["-r", args.round_id]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("apply-results-to-standings.py", *cmd_args, *unknown)

        elif cmd == "convert-excel-to-csv":
            run_script("convert-excel-to-csv.py", "--input", args.input, "--output", args.output, *unknown)

        elif cmd == "convert-table-to-excel":
            run_script("convert-table-to-excel.py", *unknown)

        elif cmd == "test":
            run_script(f"test_script{args.name[-1]}", *unknown)

        else:
            parser.print_help()

    except subprocess.CalledProcessError as e:
        print(f"Command failed: {e}", file=sys.stderr)
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
