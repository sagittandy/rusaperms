"""
Select just the multi-state perms from a CSV file containing all perms.
"""

import schemata
import csv
import argparse
import sys

schema = schemata.geolocated  # but we might not have the whole thing


parser = argparse.ArgumentParser(description="Extract CSV from RUSA perms table.")
parser.add_argument('state', help="Two-letter state abbreviation, like OR")
parser.add_argument('infile', nargs='?',
                    type=argparse.FileType('r', encoding="utf-8", errors="replace"),
                    default=sys.stdin)
parser.add_argument('outfile', nargs='?', help="CSV file output goes here",
                    type=argparse.FileType('w'), default=sys.stdout)
args = parser.parse_args()

reader = csv.reader(args.infile)
writer = csv.writer(args.outfile)

selected_state = args.state
states_pos = schema.index("Perm_states")
for row in reader:
    if row[0] == schema[0]:
        writer.writerow(row)
        continue
    if selected_state in row[states_pos]: 
               writer.writerow(row)

args.outfile.close()

    
        
