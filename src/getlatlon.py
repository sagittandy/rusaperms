#-----------------------------------------------------------------------
# (C) Copyright RUSA, 2010
#
# getlatlon.py
#
# Returns latitude and longitude information for a 'place name'.
# First searches for the information in a local CSV file.
# If the information is not present in the CSV file, 
# this program fetches from Google Maps Geocoding API, and
# appends the information to the local CSV file.
#
# The local CSV file serves as a cache of latitude and longitude values.
# This cache reduces the number of queries issued to the Google server
# and speeds performance of this program.
#
# The local CSV file may be manually edited with care in order to
# - define locations not recognized by Google, or to
# - override locations recognized incorrectly by Google.
#
# The name of the local CSV file is provided to the constructor as an arg.
# The contents 'schema' of the local CSV file is defined herein:
#     [ "Place Name", "Latitude", "Longitude" ]
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
import httplib
import sys
import time
from sop import Sop
from csvfileparser import CSVFile
import simplejson

# Logger.
mySop = Sop(3)
def sop(level,methodname,message):
    mySop.sop(level,"getlatlon/" + methodname,message)

class GetLatLon:
    def __init__(self,fileName):
        """Opens the local CSV file with place names, latitudes, and longitudes."""
        m = "GetLatLon/init:"
        sop(3,m,"Entry. fileName=%s" % ( fileName ))

        # Open and parse the local CSV file.
        ignoreStringList = [ "/", "#", '"Place Name"', '"=====' ]
        recordName = "Place Name"
        columnNameList = [ "Place Name", "Latitude", "Longitude" ]
        self.latLonDatabase = CSVFile(fileName,ignoreStringList,recordName,columnNameList)

        sop(3,m,"Exit.")

    def get(self,placeName):
        """Returns two strings, latitude and longitude, for the specified placeName.
        Returns the value found in the local CSV file, or from Google Maps.
        If fetched from Google Maps, also stores the value into the local CSV file."""
        m = "GetLatLon/get:"
        sop(5,m,"Entry. placeName=%s" % ( placeName ))

        # For verbose debug only
        # self.latLonDatabase.toString()

        # Clean up the place name.
        # Tolerate wierd sequences of spaces, single quotes, and double quotes.
        placeName = placeName.strip("'").strip('"').strip().strip("'").strip('"').strip()
        sop(5,m,"Stripped. placeName=%s" % ( placeName ))

        lat = self.latLonDatabase.get(placeName, "Latitude")
        lon = self.latLonDatabase.get(placeName, "Longitude")
        sop(5,m,"lat=%s lon=%s" % ( lat, lon ))

        if None != lat and None != lon:
            lat6 = self.getSignificantDigits(lat)
            lon6 = self.getSignificantDigits(lon)
            sop(5,m,"Exit. Returning lat/lon from local CSV file. lat6=%s lon6=%s" % ( lat6, lon6 )) 
            return lat6,lon6

        # Get new coordinates from Google.
        latLonJSON = self.getLatLonJSONForAddress(placeName)
        #sop(5,m,"After fetching from Google, latLonJSON=%s" % ( latLonJSON ))

        # Parse and extract the lat/lon from JSON response string.
        lat,lon = self.getLatLonFromGoogleJSON( latLonJSON )
        #sop(5,m,"After parsing, lat=%s lon=%s" % ( lat, lon ))

        # Add lat/lon to database propertiess file for future use.
        # (It would be nice to clean this up and abstract the 'schema'.)
        self.latLonDatabase.put( [placeName, lat, lon] )

        lat6 = self.getSignificantDigits(lat)
        lon6 = self.getSignificantDigits(lon)
        sop(5,m,"Exit. Returning lat/lon from Google. lat6=%s lon6=%s" % ( lat6, lon6 )) 
        return lat6,lon6

    def getLatLonJSONForAddress(self, address):
       """Issues an HTTP request to Google Maps Geocoding API in order to 
       fetch latitude and longitude values for a searchable address string.  
       Returns a JSON string containing latitude,longitude, etc."""
       m = "GetLatLon/getLatLonJSONForAddress:"
       sop(5,m,"Entry. address=%s" % ( address ))
       responseJSON = None

       # Trim leading and trailing whitespace.
       address = address.strip()

       # Trim leading and trailing double quotes.
       address = address.strip('"')

       # Convert all spaces in the address to plus signs.
       address = address.replace(" ","+")

       sop(5,m,"After stripping and converting, address=%s" % ( address ))

       # Define the URL to transmit to Google Maps.
       geocodeHostname = "maps.googleapis.com"
       geocodeURL = "http://%s/maps/api/geocode/json?address=%s&sensor=false" % ( geocodeHostname, address )
       sop(5,m,"geocodeURL=%s" % ( geocodeURL ))

       # Fetch
       sop(5,m,"Issuing request.")
       try:
           httpConnection = httplib.HTTPConnection(geocodeHostname)
           httpConnection.request('GET',geocodeURL)
           httpResponse = httpConnection.getresponse()
           sop(5,m,"httpResponse.status=%s" % ( httpResponse.status ))

           # Evaluate response code.
           if 200 == httpResponse.status:
               # Read response data.
               responseJSON = httpResponse.read()
               sop(5,m,"responseJSON=%s" % ( responseJSON ))
           else:
               sop(5,m,"Error. Could not fetch address information from Google Maps.")

           # Close the connection.
           httpConnection.close()
       except:
           raise m + " ERROR: Could not fetch lat/lon from Google Geocode API for address %s" % ( address )

       sop(5,m,"Exit. Returning responseJSON.")
       return responseJSON

    def getLatLonFromGoogleJSON( self, jsonString ):
        """Parses a JSON string received as a response
        from the Google Maps Geocoding API.  For example,
            { "status": "OK",
              "results": [ {"types": [ "street_address" ],
                            "formatted_address": "1600 Amphitheatre Pkwy, Mountain View, CA 94043, USA",
                            "address_components": [ { "long_name": "1600",
                                                      "short_name": "1600",
                                                      "types": [ "street_number" ]  },
                                                    { "long_name": "Amphitheatre Pkwy",
                                                      "short_name": "Amphitheatre Pkwy",
                                                      "types": [ "route" ]  },
                                                  ],
                            "geometry" : { "location": { "lat": 37.4219720,
                                                         "lng": -122.0841430 },
                                           "location_type": "ROOFTOP",
                                           "viewport": { "southwest": { "lat": 37.4188244,
                                                                        "lng": -122.0872906 },
                                                         "northeast": { "lat": 37.4251196,
                                                                        "lng": -122.0809954}}}} ]}'

        This method is hard-coded to assume: results-> geometry-> location-> lat/lon.
        This method uses python library simplejson.
        This method returns two string values: latitude,longitude"""
        m = "getLatLonFromGoogleJSON:"
        sop(5,m,"Entry.")
        sop(5,m,"jsonString=%s" % ( jsonString ))

        # Convert the JSON string into a python object.
        jsonObject = simplejson.loads( jsonString )
        #sop(5,m,"jsonObject=%s" % ( jsonObject ))

        # Verify status is 'OK'
        statusString = jsonObject["status"]
        #sop(5,m,"statusString=%s" % ( statusString ))
        if "OK" != statusString:
            raise m + " Error: Status is not OK. Status=%s" % ( statusString )

        # Extract the results list, which is expected to contain one element.
        resultsList = jsonObject["results"]
        #sop(5,m,"resultsList=%s" % ( resultsList ))
        if 1 != len(resultsList):
            sop(5,m, "WARNING: Unexpected number of elements in results list. Using first element. expected=1 actual=%i" % ( len(resultsList )))

        # Extract the first and only element.
        results = resultsList[0]
        #sop(5,m,"results=%s" % ( results ))

        # Extract the geometry element from the results.
        geometry = results["geometry"]
        #sop(5,m,"geometry=%s" % ( geometry ))

        # Extract the location from geometry.
        location = geometry["location"]
        #sop(5,m,"location=%s" % ( location ))

        # And finally, extract the latitude and longitude from the location.
        # Note the variable name translation:  lon (my preference) vs lng (Google's preference)
        lat = location["lat"]
        lon = location["lng"]
        #sop(5,m,"lat=%s lon=%s" % ( lat, lon ))

        # Convert to strings, in case they are parsed as numbers.
        latString = "%s" % ( repr(lat) )
        lonString = "%s" % ( repr(lon) )

        sop(5,m,"Exit. Returning latString=%s, lonString=%s" % ( latString, lonString ))
        return latString,lonString

    def getSignificantDigits(self, input):
        """Returns a max number of digits following the decimal point for a lat and/or lon string.
        This is done in an attempt to simplify the processing load at google maps.
        Input is a string holding what looks like a floating point number.
        Returns the same type of string."""
        m = "getSignificantDigits:"
        sop(5,m,"Entry.")
        sop(5,m,"input=%s" % ( input ))

        # Find the decimal point.
        indexPoint = input.index(".")
        sop(5,m,"indexpoint=%i" % ( indexPoint ))

        if 0 > indexPoint:
            output = input
        else:
            if len(input) < (indexPoint + 5):
                output = input
            else:
                output = input[:(indexPoint + 5)]

        sop(5,m,"Exit. Returning output=>>>%s<<< for input=%s" % ( output, input ))
        return output


#-----------------------------------------------------------------------
# main - the program starts here.
#-----------------------------------------------------------------------
# m = "getlatlon/main:"
# sop(5,m,"Entry")
# 
# # Unit testing.
# # # zips = [ "27713", "90210", "10017" ]
# # # for zip in zips:
# # #     getLatLonJSONForAddress(zip)
# # # 
# # # cityStates = [ "Durham, NC", "Hollywood, CA", "Brooklyn, NY" ]
# # # for cityState in cityStates:
# # #     getLatLonJSONForAddress(cityState)
# # 
# # getlatlon = GetLatLon("/home/ding/tmp/unittest.place.lat.lon.csv")
# # placeName = "Durham, NC"
# # lat,lon = getlatlon.get(placeName)
# # sop(5,m,"1. === Got Lat/Lon for %s. lat=%s, lon=%s" % ( placeName, lat, lon ))
# # 
# # placeName = '"Durham, NC"'
# # lat,lon = getlatlon.get(placeName)
# # sop(5,m,"2. === Got Lat/Lon for %s. lat=%s, lon=%s" % ( placeName, lat, lon ))
# # 
# # placeName = "'Durham, NC'"
# # lat,lon = getlatlon.get(placeName)
# # sop(5,m,"3. === Got Lat/Lon for %s. lat=%s, lon=%s" % ( placeName, lat, lon ))
# 
# # Convert real perm city/state info to lat/lon.
# permFileName = "/home/ding/doc/rusa/perm.map/unittest.permroutereport.number.city.state.csv"
# permIgnoreStringList = [ "/", "#", '"Place Name"', '"Route"' ]
# permColumnNameList = [ "Route Number", "Start City", "Start State" ]
# permRecordName = permColumnNameList[0]
# permroutereport = CSVFile(permFileName,permIgnoreStringList,permRecordName,permColumnNameList)
# 
# placeLatLon = GetLatLon("/home/ding/tmp/place.lat.lon.csv")
# 
# permRecordNameKeys = permroutereport.getRecordNameKeys()
# for permRecordName in permRecordNameKeys:
#     #sop(5,m,"permRecordName=%s" % ( permRecordName ))
#     permStartCity = permroutereport.get(permRecordName, "Start City")
#     permStartState = permroutereport.get(permRecordName, "Start State")
#     #sop(5,m,"startCity=%s startState=%s" % ( permStartCity, permStartState ))
# 
#     # This is an important conversion:...
#     permCityState = "%s, %s" % ( permStartCity.strip('"'), permStartState.strip('"') )
#     sop(5,m,"perm %s: %s" % ( permRecordName, permCityState ))
# 
#     # Do it.  Read location data from place.lat.lon, or get it from Google...
#     lat,lon = placeLatLon.get( permCityState )
# 
# 
# sop(5,m,"Exit")

