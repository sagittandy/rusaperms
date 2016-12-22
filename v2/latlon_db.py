"""
Latitude/Longitude database as CSV file.
Based on Andy's "csvfileparser.py", but using the
csv module of Python 3.

We'll actually use two files,
  latlon_auto.csv   # Those from Google geocoding
  latlon_manual.csv # Those manually set because geocoding failed
"""
import logging
import csv
import schemata # File layout.  Also hardwired! 
import CONFIG   # To get database location

logging.basicConfig(level=logging.INFO)

class DB:
    """
    CSV file backed map from a location like
    'Anchorage, AK' or '2110 Holiday Corndog Street, OR'
    to latitude and longitude.
    """
    def __init__(self, backing_file_path):
        self.db = { }  # Might as well be a dict
        with open(backing_file_path) as infile:
            reader = csv.reader(infile)
            for row in reader:
                logging.debug("db row {}".format(row))
                ### Some rows we ignore ... including
                ### headers, comments, and empty lines 
                if (len(row) == 0 or
                    row[0] == schemata.locations[0] or
                    row[0].startswith("#")):
                    logging.debug("db skipping {}".format(row))
                    pass
                elif len(row) == 3:
                    logging.debug("db entering {}".format(row))
                    place, lat, lon = row
                    self.db[place] = (lat, lon)
                else:
                    logging.error("Malformed row in {}:'{}'".format(backing_file_path, row))
                    
    def lookup(self,place):
        if place in self.db:
            return self.db[place]
        return (None, None)

    def insert(self, place, lat, lon):
        logging.info("DB saving info '{}' at {},{}".format(place,lat,lon))
        self.db[place] = (lat, lon)

    def save(self, to_file_path):
        logging.info("Writing augmented location database to {}"
                     .format(to_file_path))
        with open(to_file_path, 'w') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(schemata.locations)
            for place in sorted(self.db.keys()):
                lat, lon = self.db[place]
                row = [ place, lat, lon ]
                logging.debug("DB write {}".format(row))
                writer.writerow(row)
