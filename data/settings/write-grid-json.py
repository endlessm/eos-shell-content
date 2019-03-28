#!/usr/bin/env python3

from argparse import ArgumentParser
from collections import OrderedDict
import errno
import json
import os
import sys

aparser = ArgumentParser(description='Write icon grid json file')
aparser.add_argument('-o', '--output', help='output file')
aparser.add_argument('input', help='input template file')
aparser.add_argument('blacklist', help='blacklist file')
aparser.add_argument('cpu', help='CPU for blacklisting')
args = aparser.parse_args()

# Load with template and blacklist. Use OrderedDict for the grid to
# maintain sorting of the keys.
with open(args.input, 'r') as infile:
    grid = json.load(infile, object_pairs_hook=OrderedDict)
with open(args.blacklist, 'r') as blfile:
    blacklist = json.load(blfile)

# Open the a temporary version of the output file if specified, ensuring
# that leading directories are created first.
if args.output is None:
    outfile = sys.stdout
else:
    outdir = os.path.dirname(args.output)
    if len(outdir) > 0:
        try:
            os.makedirs(outdir)
        except OSError as err:
            if err.errno != errno.EEXIST:
                raise
    outfile = open(args.output + '.tmp', 'w')

# Strip out blacklisted apps
cpu_blacklist = blacklist.get(args.cpu, [])
for app in cpu_blacklist:
    if app in grid:
        del grid[app]
    for sect, apps in grid.items():
        if app in apps:
            grid[sect].remove(app)

# Write out the new json, keeping the indentation, separators and
# trailing newline from the original. If successful, rename the
# temporary file to the final name.
json.dump(grid, outfile, indent=2, separators=(',', ' : '))
outfile.write('\n')
if args.output is not None:
    outfile.close()
    os.rename(args.output + '.tmp', args.output)
