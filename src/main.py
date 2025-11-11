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
import os
from pathlib import Path


# Parse only --verbose early (before imports)
if "--verbose" in sys.argv:
    os.environ["LOG_LEVEL"] = "DEBUG"
else:
    os.environ["LOG_LEVEL"] = "INFO"

from common.logger import get_logger
logger = get_logger(__name__)

# --- Ensure project root is on sys.path ---
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


def run_script(script_rel_path, *args):
    """Run a sub-script with correct Python environment."""
    env = os.environ.copy()
    env["PYTHONPATH"] = SRC + os.pathsep + env.get("PYTHONPATH", "")
    script_path = os.path.join(SRC, script_rel_path)
    subprocess.run([sys.executable, script_path, *args], check=True, env=env)


def main():
    parser = argparse.ArgumentParser(
        description="Swiss System Tournament Manager CLI"
    )
    parser.add_argument("--verbose", "-v",
                        action="store_true",
                        help="Enable verbose logging")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # --- Command definitions ---

    subparsers.add_parser("init-db", help="Initialize the tournament database")
    subparsers.add_parser("generate-players", help="Generate list of players")
    subparsers.add_parser("register-players", help="Register players into the database")

    p = subparsers.add_parser("generate-swiss-pairings", help="Generate swiss match pairings")
    p.add_argument("-r", "--round-id", required=True, help="Round ID")

    p = subparsers.add_parser("generate-roundrobin-pairings", help="Generate round-robin match pairings")
    
    subparsers.add_parser("register-standings", help="Register tournament standings")

    p = subparsers.add_parser("populate-results", help="Populate results from a file")
    p.add_argument("-f", "--file", required=True, help="CSV file with results")

    p = subparsers.add_parser("register-results", help="Register results into DB")
    p.add_argument("-f", "--input-file", required=True, help="Results input CSV file")
    p.add_argument("--conn", help="PostgreSQL connection string")

    p = subparsers.add_parser("print-table", help="Print tournament tables")
    p.add_argument("-t", "--table", choices=["standings", "results", "players"], required=True)
    p.add_argument("--conn", help="PostgreSQL connection string")

    p = subparsers.add_parser("apply-results", help="Apply results to standings for a given round")
    p.add_argument("-r", "--round-id", required=True)
    p.add_argument("--conn", help="PostgreSQL connection string")

    p = subparsers.add_parser("convert-excel-to-csv", help="Convert Excel file to CSV format")
    p.add_argument("--input", default="data/input.xlsx", help="Path to input Excel file")
    p.add_argument("--output", default="data/output.csv", help="Path to output CSV file")

    subparsers.add_parser("convert-table-to-excel", help="Convert DB tables to Excel format")

    test_parser = subparsers.add_parser("test", help="Run internal test scripts")
    test_parser.add_argument(
        "name",
        choices=["test_pairings", "test_player", "test_standings", "test_tournament"],
        help="Test script name (e.g., test_pairings)"
    )

    # --- Parse args ---
    args, unknown = parser.parse_known_args()
    cmd = args.command
    
    # Ignore --verbose if already present
    unknown = [u for u in unknown if u not in ("--verbose", "-v")]

    try:
        # --- Core scripts ---
        if cmd == "init-db":
            run_script("core/init_db.py", *unknown)

        elif cmd == "generate-players":
            run_script("core/generate-players.py", *unknown)

        elif cmd == "register-players":
            run_script("core/register-players.py", *unknown)

        elif cmd == "generate-roundrobin-pairings":
            run_script("core/generate-roundrobin-pairings.py", *unknown)

        elif cmd == "generate-swiss-pairings":
            run_script("core/generate-swiss-pairings.py", "-r", args.round_id, *unknown)

        elif cmd == "register-standings":
            run_script("core/register-standings.py", *unknown)

        elif cmd == "populate-results":
            run_script("utils/populate-results.py", "-f", args.file, *unknown)

        elif cmd == "register-results":
            cmd_args = ["-f", args.input_file]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("core/register-results.py", *cmd_args, *unknown)

        elif cmd == "apply-results":
            cmd_args = ["-r", args.round_id]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("core/apply-results-to-standings.py", *cmd_args, *unknown)

        # --- Utility scripts ---
        elif cmd == "print-table":
            cmd_args = ["-t", args.table]
            if args.conn:
                cmd_args += ["--conn", args.conn]
            run_script("utils/print-table.py", *cmd_args, *unknown)

        elif cmd == "convert-excel-to-csv":
            run_script("utils/convert-excel-to-csv.py", "--input", args.input, "--output", args.output, *unknown)

        elif cmd == "convert-table-to-excel":
            run_script("utils/convert-table-to-excel.py", *unknown)

        # --- Test scripts ---
        elif cmd == "test":
            run_script(f"test/{args.name}.py", *unknown)

        else:
            parser.print_help()

    except subprocess.CalledProcessError as err:
        logger.error("Subcommand failed: %s", err)
        sys.exit(err.returncode)
    except FileNotFoundError as err:
        logger.error("Script not found: %s", err)
        sys.exit(1)
    except Exception as err:
        logger.error("Unexpected error occurred! %s", err)
        sys.exit(1)





if __name__ == "__main__":
    main()
