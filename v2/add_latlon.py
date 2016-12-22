"""
Add latlon values to table of permanents

pipeline or workflow: 
   snarf => addlatlon => convert to html+js

Input and output of this state is a CSV file; we're adding two
new columns on the left.

"""
import getlatlon
import schemata

import sys # For stdin, stdout
import csv
import logging
logging.basicConfig(level=logging.INFO)


geocoder = getlatlon.GetLatLon(extend=True)

def addLatLon(record):
    """
    We assume first two columns are state and city, and we use
    that to do Geocoding lookup.
    """
    state = record[0]
    city = record[1]
    placename = "{}, {}".format(city, state)
    logging.debug("Looking up {}".format(placename))
    lat, lon = geocoder.get(placename)
    logging.debug("Got location {},{}".format(lat,lon))
    record.append(lat)
    record.append(lon)
    logging.debug("Decorated: {}".format(record))
    return record

def decorate(csv_in, csv_out):
    for record in csv_in:
        if (len(record)==0 or
            record[0].startswith("#") or
            record[0] == schemata.rusa_snarf[0]):
            continue
        decorated = addLatLon(record)
        logging.debug("Decorated as {}".format(decorated))
        csv_out.writerow(decorated)
    
    

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Geolocate permanent list")
    parser.add_argument('input', help="The CSV file without latlon information",
                        type=argparse.FileType('r'),
                        nargs="?", default=sys.stdin)
    parser.add_argument('output', help="The CSV file to write decorated CSV on",
                        type=argparse.FileType('w'),
                        nargs="?", default=sys.stdout)
    args = parser.parse_args()
    reader = csv.reader(args.input)
    writer = csv.writer(args.output)
    writer.writerow(schemata.geolocated)
    decorate(reader, writer)
    geocoder.close()
