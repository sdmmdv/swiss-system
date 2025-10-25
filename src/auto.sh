#!/usr/bin/env bash
# Usage: ./run_round.sh <round_number>
# Example: ./run_round.sh 4

# Exit on error
set -e

# Read round number from first argument
ROUND_ID="$1"

# Validate argument
if [ -z "$ROUND_ID" ]; then
  echo "Usage: $0 <round_number>"
  exit 1
fi

# Generate pairings for the given round
./main.py generate-pairings -r "$ROUND_ID" -t "roundrobin"

# Populate results using generated pairings file
./main.py populate-results -f "../data/pairings_r${ROUND_ID}.csv"

# Register results for the round
./main.py register-results -f "../data/results_r${ROUND_ID}.csv"

# Apply results (update standings)
./main.py apply-results -r "$ROUND_ID"

# Print the standings table
./main.py print-table -t standings

