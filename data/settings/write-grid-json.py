#!/usr/bin/env python3

from argparse import ArgumentParser, FileType
import json
import os
import sys

aparser = ArgumentParser(description='Write icon grid json file')
aparser.add_argument('-o', '--output', help='output file')
aparser.add_argument('input', help='input template file', type=FileType("r"))
args = aparser.parse_args()

# Load template
grid = json.load(args.input)

# Open the a temporary version of the output file if specified, ensuring
# that leading directories are created first.
if args.output is None:
    outfile = sys.stdout
else:
    outdir = os.path.dirname(args.output)
    if len(outdir) > 0:
        os.makedirs(outdir, exist_ok=True)
    outfile = open(args.output + '.tmp', 'w')

# Check that all directories are in the top-level "desktop" pseudo-directory
desktop = grid["desktop"]
for directory in grid:
    if directory != "desktop" and directory not in desktop:
        raise ValueError(
            '"{}" defined but not in "desktop" directory'.format(directory)
        )

# Write out the new json, keeping the indentation, separators and
# trailing newline from the original. If successful, rename the
# temporary file to the final name.
json.dump(grid, outfile, indent=2, separators=(',', ' : '))
outfile.write('\n')
if args.output is not None:
    outfile.close()
    os.rename(args.output + '.tmp', args.output)
