"""
Generate html from CSV file of RUSA perms.

We assume the input CSV file is sorted by location and then distance.
The snarf step ensures sorting by location.  Documentation doesn't
say anything about sorting by distance, but this seems to be its behavior.
If this changes in the future, we may need to impose a sorting-and-bucketing
step. 
"""
import schemata
import sys
import csv
import html 
import logging
logging.basicConfig(level=logging.INFO)

# Boilerplate before and after the part we generate 


#
# The part we generate looks like
#

       # var marker = L.marker([44.7748, -117.8343],
       #      title="Baker City Grand Flop",
       #      alt="Baker City Grand Flap"
       #      ).bindPopup("here's my popup").addTo(mymap);


marker_template="""
       var marker = L.marker([{latitude}, {longitude}],
           {{ 
              title: "{title}",
              alt: "{title}",
              icon: {icon}
           }}
            ).bindPopup("<div><p>{owner}</p>" +
                  "<p><a href={href}>{title}</a></p>" +
                  "<p>{dist}km</p>" + 
                  "<p>{notes}</p>" +
                  "</div>");
      markers.addLayer(marker);
"""

def marker(record):
    """
    For convenience we take the record as a dict.
    """
    logging.debug("Formatting record {}".format(record))
    perm_dist = int(record["Perm_km"])
    icon = "icon100" # as default
    for distance in [1200, 1000, 600, 400, 300, 200, 100]:
        if perm_dist >= distance:
            icon = "icon{}".format(distance)
            break

    js = marker_template.format(latitude=record["Lat"],
                                longitude=record["Lon"],
                                icon=icon,
                                title=html.escape(record["Perm_name"]),
                                owner=record["Perm_owner"],
                                dist=record["Perm_km"], 
                                href=record["Href"],
                                notes=record["Perm_notes"])
    return js
                                
    
def copy_to_output(path, output):
    """
    Copy the boilerplate files without change.
    Path is a string, output is an open file. 
    """
    with open(path, 'r') as input:
        for line in input:
            print(line, file=output, end="")
    

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate html from geocoded perms")
    parser.add_argument('input', help="The CSV file with geocoding",
                        type=argparse.FileType('r'),
                        nargs="?", default=sys.stdin)
    parser.add_argument('output', help="The html file to write",
                        type=argparse.FileType('w'),
                        nargs="?", default=sys.stdout)
    parser.add_argument('--limit', type=int, help="Produce only a few entries",
                         nargs='?', default=0)
    args = parser.parse_args()
    reader = csv.DictReader(args.input)

    copy_to_output("boilerplate/leaflet_prolog.html", args.output)
    count = 0
    for record in reader:
        print(marker(record), file=args.output, end="")
        count += 1
        if args.limit and count >= args.limit:
            logger.info("Cutting off at {} permanents".format(count))
            break
    copy_to_output("boilerplate/leaflet_postlog.html", args.output)


if __name__ == "__main__":
    main()


    
    
