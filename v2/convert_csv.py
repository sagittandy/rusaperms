"""
Convert RUSA Perms report CSV to
the CSV format we'll use for mapping.

Besides selecting and renaming columns, the
transformations are:

* Inactive routes are omitted
* If a route is reversible AND point-to-point,
  it is duplicated with from and two locations
  reversed

"""

import csv
import sys
import schemata

schema_in = schemata.rusa_report
schema_out = schemata.rusa_snarf


def process(record, output):
    """
    Row is in form of a dict, to minimize dependence on schema,
    although we still depend on the fields we need being present.

    Output is also through a dictwriter, driven by the schema.  If
    we have not matched the schema.
    """
    if not record["Active?"]:
        return
    outrow = { }
    outrow["Perm_id"] = record["Route #"]
    outrow["State"] = record["Start State"].strip()
    outrow["City"] = record["Start City"].strip()
    outrow["Perm_km"] = record["Distance"]
    name_parts = record["Route name"].split(":")
    outrow["Perm_name"] = name_parts[1].strip()
    outrow["Perm_owner"] = record["Owner Name"]
    outrow["Perm_notes"] = extract_notes(record).strip()
    outrow["Perm_states"] = record["Within State(s)"]
    output.writerow(outrow)
    ## Also the reversed route? 
    if record["Type"] == "PP" and record["Reversible?"] == "Y":
        outrow["State"] = record["End State"].strip()
        outrow["City"] = record["End City"].strip()
        outrow["Perm_notes"] = extract_notes(record, reverse=True)
        output.writerow(outrow)

def extract_notes(record, reverse=False):
    """
    Synthesize notes from record fields.
    """
    notes = ""
    sep = ""
    if record["Type"] == "PP":
        if  reverse: 
            notes += "(Reversed) to {}, {}".format(
                record["Start City"], record["Start State"])
        else:
            notes += "to {}, {}".format(
                record["End City"], record["End State"])
        sep = "; "
    if record["Free-route?"] == "yes":
        notes += sep + "Free-route"
        sep = ";"
    if record["Super Randonn&eacute;e?"] == "yes":
        notes += sep + "Super randonn&eacute;e"
        sep = ";"
    return notes

def main(reader, writer):
    writer.writeheader()
    for row in reader:
        process(row,writer)

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
    reader = csv.DictReader(args.input)
    writer = csv.DictWriter(args.output, schema_out)
    main(reader,writer)
    args.output.close()

