"""
Obtain the RUSA perms records
"""
import requests
import simplejson as json

import csv
import io
import sys

from typing import List,  Dict

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

RUSA_PERMS_URL="https://rusa.org/cgi-bin/gdbm2json.pl?permanents"
#  For a state: ?permanents&startstate=OR

CSV_SCHEMA = ["pid", "name", "dist", "description", "url"]

# Route = namedtuple('Route', CSV_SCHEMA)

def get(start_state=None) -> list:
    """Fetch JSON record of the whole collection"""
    # Login here if required; currently not working
    log.debug(f"Callinq RUSA service")
    params = {}
    if start_state:
        params = {"startstate": start_state}
    r = requests.get(RUSA_PERMS_URL, params, verify=False)
    return r.json()

def extract(raw_json: List[Dict]) -> List[List[str]]:
    """Convert the raw json from RUSA site into
    a list of tuples with the information that we store.
    """
    result = []
    for entry in raw_json:
        if entry["status"] != "1" or entry["url"] == "":
            continue
        fields = []
        for field in CSV_SCHEMA:
            fields.append(entry[field])
        result.append(fields)
    return result


def plug(d: dict, f: List[str]):
    for field in f:
        if field not in d:
            d[field] = f"***MISSING {field}***"


def dump(entries: list):
    for entry in entries:
        if entry["status"] == "1":
            plug(entry, ["statelist", "startcity", "dist", "name"])
            print(f"{entry['statelist']} {entry['startcity']} {entry['dist']}k: {entry['name']}"
                  f"\t{entry['url']}")

def save_as_csv(entries: List[List[str]], f: io.IOBase):
    """Write tuples  to CSV file"""
    writer = csv.writer(f)
    writer.writerow(CSV_SCHEMA)
    for entry in entries:
        # row = [entry[key] for key in CSV_SCHEMA]
        writer.writerow(entry)

def dump_fields(entry: dict):
    assert isinstance(entry, dict)
    print("Keys")
    for key in entry:
        print(f"{key}  ('{entry[key]}')")

def main():
    data = get("OR")
    assert isinstance(data, list)
    converted = extract(data)
    save_as_csv(converted, sys.stdout)

# Notes:
#  Example multi-state statelist is "ID:MT:WA:OR"; always
#  a string but colon-separated.

if __name__ == "__main__":
    main()
