#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
import json
import os
import sys
import glob

def check(filename):
    print(f"Checking {filename}")

    # Load template
    with open(filename) as f:
        grid = json.load(f)

    # Check that all directories are in the top-level "desktop" pseudo-directory
    desktop = grid["desktop"]
    for directory in grid:
        if directory != "desktop" and directory not in desktop:
            raise ValueError(
                '"{}" defined but not in "desktop" directory'.format(directory)
            )

def main():
    aparser = ArgumentParser(description='Validate icon grid JSON files')
    aparser.add_argument('input',
                         help='input template file (default: all grid files in script directory)',
                         nargs="*")
    args = aparser.parse_args()

    if not args.input:
        args.input = glob.glob(
            os.path.dirname(__file__) + "/icon-grid-*.json",
        )

    for filename in args.input:
        check(filename)

if __name__ == "__main__":
    main()
