def getLatLonJSONForAddress(self, address):
    """Issues an HTTP request to Google Maps Geocoding API in order to
    fetch latitude and longitude values for a searchable address string.
    Returns a JSON string containing latitude,longitude, etc."""
    m = "GetLatLon/getLatLonJSONForAddress:"
    logging.debug("Entry. address={}".format(address))
    responseJSON = None

    # Trim leading and trailing whitespace.
    address = address.strip()

    # Trim leading and trailing double quotes.
    address = address.strip('"')

    # Convert all spaces in the address to plus signs.
    address = address.replace(" ", "+")

    logging.debug("After stripping and converting, address={}".format(address))

    # Define the URL to transmit to Google Maps.
    geocodeHostname = "maps.googleapis.com"
    geocodeURL = ("http://{}/maps/api/geocode/json?address={}&sensor=false"
                  .format(geocodeHostname, address))
    logging.debug("geocodeURL={}".format(geocodeURL))

    # Fetch
    # (MY mod:  sleep 0.15 seconds for rate limiting)
    logging.info("Sleeping to stay within rate limits")
    time.sleep(1.0)  # Google rate limit is 2500 per day or 10 per second
    logging.info("Woke up")
    logging.info("Issuing request.")
    try:
        logging.info("Making http connection")
        httpConnection = http.client.HTTPConnection(geocodeHostname)
        httpConnection.request('GET', geocodeURL)
        httpResponse = httpConnection.getresponse()
        logging.debug("httpResponse.status={}".format(httpResponse.status))

        # Evaluate response code.
        if 200 == httpResponse.status:
            # Read response data.
            responseJSON = httpResponse.read()
            # logging.debug("responseJSON={}".format( responseJSON ))
        else:
            logging.error("Error. Could not fetch address information from Google Maps.")

        # Close the connection.
        httpConnection.close()
    except:
        raise RuntimeError(m + " ERROR: Could not fetch lat/lon from Google Geocode API for address {}".format(address))

    logging.debug("Exit. Returning responseJSON.")
    return responseJSON


def getLatLonFromGoogleJSON(self, jsonString):
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
    # logging.info("Entry.")
    # logging.debug("jsonString={}".format( jsonString ))

    # Convert the JSON string into a python object.
    jsonObject = simplejson.loads(jsonString)

    # Verify status is 'OK'
    statusString = jsonObject["status"]
    if "OK" != statusString:
        raise RuntimeError(m + " Error: Status is not OK. Status=%s" % (statusString))

    # Extract the results list, which is expected to contain one element.
    resultsList = jsonObject["results"]
    if 1 != len(resultsList):
        logging.warn("WARNING: Unexpected number of elements " +
                     " in results list. Using first element. " +
                     "expected=1 actual={}".format(len(resultsList)))

    # Extract the first and only element.
    results = resultsList[0]

    # Extract the geometry element from the results.
    geometry = results["geometry"]

    # Extract the location from geometry.
    location = geometry["location"]

    # And finally, extract the latitude and longitude from the location.
    # Note the variable name translation:  lon (my preference) vs lng (Google's preference)
    lat = location["lat"]
    lon = location["lng"]

    # Convert to strings, in case they are parsed as numbers.
    latString = "%s" % (repr(lat))
    lonString = "%s" % (repr(lon))

    return latString, lonString


def getSignificantDigits(self, input):
    """Returns a max number of digits following the decimal point for a lat and/or lon string.
    This is done in an attempt to simplify the processing load at google maps.
    Input is a string holding what looks like a floating point number.
    Returns the same type of string."""
    m = "getSignificantDigits:"

    # Find the decimal point.
    indexPoint = input.index(".")

    if 0 > indexPoint:
        output = input
    else:
        if len(input) < (indexPoint + 5):
            output = input
        else:
            output = input[:(indexPoint + 5)]
    return output

