"""
Select just the multi-state perms from a CSV file containing all perms.
"""

import schemata
import csv
import argparse
import sys

schema = schemata.geolocated  # but we might not have the whole thing
states_pos = schema.index("Perm_states")

parser = argparse.ArgumentParser(description="Extract CSV from RUSA perms table.")
parser.add_argument('min_km', type=int, help="Minimum distance in km")
parser.add_argument('max_km', type=int, help="Maximum distance in km")
parser.add_argument('infile', nargs='?',
                    type=argparse.FileType('r', encoding="utf-8", errors="replace"),
                    default=sys.stdin)
parser.add_argument('outfile', nargs='?', help="CSV file output goes here",
                    type=argparse.FileType('w'), default=sys.stdout)
args = parser.parse_args()

reader = csv.reader(args.infile)
writer = csv.writer(args.outfile)

dist_pos = schema.index("Perm_km")
for row in reader:
    if row[0] == schema[0]:
        writer.writerow(row)
        continue
    # Distance entry should be like 200 but is sometimes like
    # 200km or 200k
    dist_text = row[dist_pos].strip(" km")
    km = int(dist_text)
    if  km >= args.min_km and km <= args.max_km:
               writer.writerow(row)

args.outfile.close()

    
        
