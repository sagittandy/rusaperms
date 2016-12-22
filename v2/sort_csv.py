"""
Sort the CSV report by location and distance,
  so that in subsequent steps we can group and
  summarize
"""

import csv
import sys
import schemata

schema = schemata.rusa_snarf

state_pos = schema.index("State")
city_pos = schema.index("City")
dist_pos = schema.index("Perm_km")

def keyfields(record):
    return "{} {} {}".format(record[state_pos],
                             record[city_pos],
                             record[dist_pos])
def main(reader, writer):
    records = [ ]
    for row in reader:
        records.append(row)
    records = sorted(records[1:], key=keyfields)
    writer.writerow(schema)
    for row in records:
        writer.writerow(row)
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Prepare RUSA CSV report")
    parser.add_argument('input', help="PermReport in CSV form directly from RUSA",
                        type=argparse.FileType('r', encoding="utf-8", errors="replace"),
                        nargs="?", default=sys.stdin)
    parser.add_argument('output', help="Output CSV in the format accepted by add_latlon",
                        type=argparse.FileType('w'),
                        nargs="?", default=sys.stdout)
    args = parser.parse_args()
    reader = csv.reader(args.input)
    writer = csv.writer(args.output)
    main(reader,writer)
    args.output.close()

