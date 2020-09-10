"""Access to a single route on RWGPS, by route number"""

import requests
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

BASE_URL = "https://ridewithgps.com"

class Authorization:
    """We start with email, password, and api_key,
    and refresh the token as needed.
    """
    def __init__(self, email: str, password: str, api_key: str):
        self.email = email
        self.password = password
        self.api_key = api_key
        log.debug("Getting initial token")
        self.token: str = get_token(email, password, api_key)
        log.debug(f"Initial auth token is {self.token}")

    def refresh(self):
        log.debug(f"Refreshing token for {self.email}")
        self.token = get_token(self.email, self.password, self.api_key)
        log.debug(f"Refreshed token is {self.token}")


def get_token(email: str, password: str, api_key: str) -> str:
    token_url = (f"{BASE_URL}/users/current.json?" +
                 f"email={email}&password={password}" +
                 f"&apikey={api_key}&version=2")

    response = requests.get(token_url)
    as_json = response.json()
    log.debug(f"Response to token URL is {response}")
    log.debug(f"Response content: {as_json}")

    return response.json()['user']['auth_token']

def get_route_json(auth: Authorization, route_id: str) -> dict:
    """Retrieve route details"""
    url = f"{BASE_URL}/routes/{route_id}.json"
    request_params = {"apikey": auth.api_key,
                    "version": "2",
                    "auth_token": auth.token}
    # response = requests.get(url, params=request_params)
    response = requests.get(url)
    log.debug(f"Route URL is {url} with parameters {request_params}")
    log.debug(f"Route request response is {response}")
    log.debug(f"Route request response content is {response.json()}")
    # Need check for expiration here ... not sure what it
    # looks like.  We'll print the actual response the
    # first time it expires.

    return response.json()

def get_route_gpx(route_id: str) -> str:
    """Gets the GPX representation of a route"""
    url = f"{BASE_URL}/routes/{route_id}.gpx"
    response = requests.get(url)
    return response.text

def main():
    """Dummy example"""
    example = get_route_gpx("33883590")
    print(example)

if __name__ == "__main__":
    main()

#
# auth = Authorization("michal.young@gmail.com",
#                   "Mock Turtle",
#                   "f631be531")
# route = get_route_json(auth, "33883590") # Birch/Hendricks short
# # print(route)
# start_point = route["track_points"][0]
# print(start_point)
# for track_point in route["track_points"]:
#     print(track_point["x"], track_point["y"])


# Note: course_points is list of cues
# {
#         "d": 1365.17,
#         "i": 3,
#         "n": "Turn left at SW Cameron Rd",
#         "t": "Left",
#         "x": -122.72318,  (lon)
#         "y": 45.4835      (lat)
#       },