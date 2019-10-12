#-----------------------------------------------------------------------
# (C) Copyright RUSA, 2010, 2016
#
#
# The local CSV file serves as a cache of latitude and longitude values.
# This cache reduces the number of queries issued to the Google server
# and speeds performance of this program.
#
#-----------------------------------------------------------------------
# Design secrets...
#
# This code issues a web request to the Google Geocoding API.  For example, 
#    maps.googleapis.com/maps/api/geocode/json?address=75+Eagle+Ridge+Place,+Danville,+CA&sensor=false
#
# A string in JSON format is received as a response.  For example, 
#   { "status": "OK",
#     "results": [ {"types": [ "street_address" ],
#                   "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
#                   "address_components": [ { "long_name": "1600",
#                                             "short_name": "1600",
#                                             "types": [ "street_number" ]  },
#                                           { "long_name": "Amphitheatre Pkwy",
#                                             "short_name": "Amphitheatre Pkwy",
#                                             "types": [ "route" ]  },
#                                         ],
#         --->      "geometry" : { "location": { "lat": 37.4219720,
#         --->                                   "lng": -122.0841430 },
#                                  "location_type": "ROOFTOP",
#                                  "viewport": { "southwest": { "lat": 37.4188244,
#                                                               "lng": -122.0872906 },
#                                                "northeast": { "lat": 37.4251196,
#                                                               "lng": -122.0809954}}}} ]}'
#
# This code parses the JSON response and assimilates the 'geometry' values.
#-----------------------------------------------------------------------
import http.client
import sys
import time
import simplejson
import latlon_db
import logging
import geocoder_mapquest as geocoder

logging.basicConfig(level=logging.INFO)

import CONFIG  # Default homes of the databases 

class GetLatLon:
    def __init__(self,
                 db_manual_path=CONFIG.latlon_manual_csv_file,
                 db_auto_path=CONFIG.latlon_auto_csv_file,
                 extend=True):
        """Opens the local CSV file with place names, latitudes, and longitudes."""
        self.db_manual = latlon_db.DB(db_manual_path)
        self.db_auto = latlon_db.DB(db_auto_path)
        self.extend_database = extend

    def close(self):
        logging.info("Closing down")
        if self.extend_database:
            self.db_auto.save(CONFIG.latlon_auto_csv_file)

    def _db_lookup(self,place):
        """
        Manually entered locations take precedence
        (Internal method)
        """
        lat, lon = self.db_manual.lookup(place)
        if lat:
            logging.debug("Found {} in manual db".format(place))
            return lat, lon
        logging.debug("Looking for {}  in auto database".format(place))
        return self.db_auto.lookup(place)
        

    def get(self,placeName):
        """Returns two strings, latitude and longitude, for the specified placeName.
        Returns the value found in the local CSV file, or from Google Maps.
        If fetched from Google Maps, also stores the value into the local CSV file."""
        m = "GetLatLon/get:"
        logging.debug("Entry. placeName={}".format( placeName ))

        # Clean up the place name.
        # Tolerate wierd sequences of spaces, single quotes, and double quotes.
        prior = "#Very unlikely string"
        while prior != placeName:
            prior = placeName
            placeName = placeName.strip(" \"'-")
        logging.debug("Stripped place name: |{}|".format(placeName))
        lat, lon = self._db_lookup(placeName)
        if lat:
            logging.debug("getlatlon: Found {} in database".format(placeName))
            # lat6 = self.getSignificantDigits(lat)
            # lon6 = self.getSignificantDigits(lon)
            logging.debug("Exit. Returning lat/lon from local CSV file." +
                          " lat={} lon={}".format( lat, lon ))
            return lat,lon

        logging.debug(f"getlatlon: {placeName} not in database, resorting to" +
                          " geocode service")
        # Get new coordinates from Google.
        # latLonJSON = self.getLatLonJSONForAddress(placeName)
        # Parse and extract the lat/lon from JSON response string.
        #lat,lon = self.getLatLonFromGoogleJSON( latLonJSON )
        lat, lon = geocoder.get_latlon(placeName)

        # Add lat/lon to database propertiess file for future use.
        # (It would be nice to clean this up and abstract the 'schema'.)
        logging.info("Recording new location info for {} at {},{}"
                     .format(placeName, lat, lon))
        self.db_auto.insert(placeName, lat, lon)
        self.extend_database = True

        #lat6 = self.getSignificantDigits(lat)
        # lon6 = self.getSignificantDigits(lon)
        logging.debug("Exit. Returning lat/lon from geocoder" +
                      " lat={} lon={}".format(lat, lon))
        return lat,lon


