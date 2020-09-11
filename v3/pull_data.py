""" Pull data from RUSA and RWGPS; populates 'data' directory.
"""
import rusa_perms
# import query_rwgps_route  # Key lines duplicated instead
import gpxpy
# import gpx_simplify

import requests
import sys
import pathlib
import json
import csv

import argparse

import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# We will write augmented CSV file:
# Selected fields from RUSA database plus lat, lon from RWGPS
CSV_SCHEMA = rusa_perms.CSV_SCHEMA + ["lat", "lon"]

# Maximum deviation from exact route
# for compressed points lists
ROUTE_DELTA = 100.0


def pull_state(state: str):
    """Pulls data for one state, producing
    data/{state}.csv (always) and, for each
    route that doesn't already have data/gpx/{route}.gpx,
    produces data/gpx/{route}.gpx and data/points/{route}.json
    """
    routes = rusa_perms.extract(rusa_perms.get(state))

    # For each route R, we create data/gpx/r.gpx (complete)
    # and data/points/r.json (simplified), and we save the
    # start point of the route in the routes table
    count_new = 0
    count_skipped = 0
    count_failed = 0
    # Indexes of fields in schema
    pid_idx = CSV_SCHEMA.index("pid")
    url_idx = CSV_SCHEMA.index("url")
    name_idx = CSV_SCHEMA.index("name")
    # Route location info - starting lat lon and full points list
    for route in routes:
        pid = route[pid_idx]
        url = route[url_idx]
        gpx_path = pathlib.Path("data/gpx", f"{pid}.gpx")
        points_path = pathlib.Path("data/points", f"{pid}.json")
        if gpx_path.exists():
            log.debug(f"{gpx_path} exists; skipping")
            # But I need starting point!
            with open(points_path) as f:
                points = json.load(f)
                lat, lon = points[0]
                route.append(lat)
                route.append(lon)
            count_skipped += 1
            continue
        try:
            log.info(f"Fetching route info for {pid} {route[name_idx]}")
            rwgps_response = requests.get(url + ".gpx")
            gpx_str = rwgps_response.text
            # Attempt to parse
            gpx_obj = gpxpy.parse(gpx_str)
            # Save raw, full GPX as data/gpx/routenum.gpx
            # (only if parsing succeeded)
            with open(gpx_path, "w") as gpx_file:
                gpx_file.write(gpx_str)
                gpx_file.write("\n")
            # Extract points after simplification
            gpx_obj.simplify(ROUTE_DELTA)
            points = gpx_points(gpx_obj)
            with open(points_path, 'w') as f:
                json.dump(points, f)
            # And add starting lat lon to table of routes
            lat, lon = points[0]
            route.append(lat)
            route.append(lon)
            count_new += 1
        except Exception as e:
            log.warning(f"Failed on rusa route {pid}, URL {url}")
            print(e, file=sys.stderr)
            count_failed += 1
    # Stash the whole table with appended lat, lon info as STATE.csv
    save_path = pathlib.Path("data", f"{state}.csv")
    with open(save_path, "w") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_SCHEMA)
        for route in routes:
            writer.writerow(route)

    log.info(f"{state} {count_new} new GPX files, {count_skipped} kept"
             + f" {count_failed} failed")


def gpx_points(gpx_obj):
    """
    Extract all the track points from a gpx object.
    Returns a list of points, each as [lat, lon]
    """
    li = []
    for track in gpx_obj.tracks:
        for segment in track.segments:
            for point in segment.points:
                li.append([point.latitude, point.longitude])
    return li


def cli() -> object:
    """Command line arguments"""
    parser = argparse.ArgumentParser(description="Pull perm routes info for a state")
    parser.add_argument('state', help="Two-letter state abbreviation, like OR")
    args = parser.parse_args()
    return args


def main():
    command = cli()
    pull_state(command.state)


if __name__ == "__main__":
    main()
