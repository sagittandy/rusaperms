"""
Geocoding service.  The intent is that while we have different 
services (Goodle, Mapquest, ...), they all have a common API so that
we can write 
   import geocoder_x as geocoder
and change only one line to get 
   import geocoder_y as geocoder

The original from SagitAndy was for Google, so we use that one 
as the model for others. 

See notes on MapQuest JSON format at end of this file. 
"""

import requests
import simplejson as json

from typing import Tuple

import logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

MAPQUEST_KEY = "X9aDA1kRtF0pQdoHF4bAlU2Gj6l1Jmye"
SERVICE_URL = "http://www.mapquestapi.com/geocoding/v1/address"


def query_mapquest(address: str) -> str:
    """Returns query result as dict/list object extracted from JSON,
    or raises exception.
    """
    log.debug(f"Callinq Mapquest service on '{address}'")
    r = requests.get(SERVICE_URL, params={"key": MAPQUEST_KEY,
                                           "location": address,
                                           "maxResults": 1
                                          })
    result = r.json()
    # result_dict = json.loads(result)
    # status = result_dict[info][statuscode]
    status = result["info"]["statuscode"]
    log.debug(f"Mapquest status code {status}")
    if status != 0 :
        log.warning(f"Non-zero status from Mapquest geocoder: {result['info']}")
        raise RuntimeError("MapQuest geocoding error: {result['info']}")
    return r.json()

def get_latlon(address: str) -> Tuple[float, float]:
    """MapQuest geocoding of address"""
    result = query_mapquest(address)
    latlon = result["results"][0]["locations"][0]["latLng"]
    return latlon['lat'], latlon['lng']


