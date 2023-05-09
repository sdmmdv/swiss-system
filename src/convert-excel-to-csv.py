#!/usr/bin/env python3

from pathlib import Path
import pandas as pd
import argparse
import os

def root_dir() -> Path:
    return Path(__file__).resolve().parent.parent

def convert_to_csv(input_file, output_file):
    # Load the Excel file using pandas
    df = pd.read_excel(input_file)

    # Save the data to a CSV file
    df.to_csv(output_file, index=False)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--input',
                        default=root_dir() / 'data/input.xlsx',
                        help=f'Input Excel file (default: %(default)s)')
    parser.add_argument('--output',
                        default=root_dir() / 'data/output.csv',
                        help=f'Output CSV file (default: %(default)s)')
    args = parser.parse_args()

    # Convert the Excel file to CSV
    convert_to_csv(args.input, args.output)

if __name__ == '__main__':
    main()
