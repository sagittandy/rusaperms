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




def distance_group(record):
    """Rather than group exact distances, we'll group
       by distance class.
    """
    perm_dist = int(record["Perm_km"])
    for distance in [1200, 1000, 600, 400, 300, 200, 100]:
        if perm_dist >= distance:
            return distance
    return 100

# Control break logic --- we'll keep a list of records and
# produce a summary pin when location or distance bucket changes
group = [ ]
prior = [ ]

def accumulate(record, output):
    """
    Control break logic:  Adds current record to
    the current group, after potentially dumping and
    restarting the current group.
    """
    global group
    global prior
    dist_group = distance_group(record)
    record["Dist_group"] = dist_group
    grouping = [ record["Lat"], record["Lon"], dist_group ]
    if grouping != prior:
        flush(output)
        prior = grouping
    group.append(record)

def flush(output):
    global group
    emit_group(group, output)
    group = [ ]


marker_group_template ="""
       var marker = L.marker([{latitude}, {longitude}],
           {{ 
              title: "{title}",
              alt: "{title}",
              icon: {icon},
              count: {count}
           }}
            ).bindPopup("<div><p>{title}</p>" +
                        "<p>{desc}</p>" +
                        "</div>");
      markers.addLayer(marker);
"""

def perm_in_group(record):
    notes = record["Perm_notes"]
    if len(notes) > 0:
        notes = " ({})".format(notes)
    desc = ("<br /><a href={href}>{title}</a> {owner} {notes}"
          .format(title=html.escape(record["Perm_name"]),
                  owner=record["Perm_owner"],
                  href=record["Href"],
                  notes=record["Perm_notes"]))
    return desc

def emit_group(group, output): 
    logging.debug("Emitting group: {}".format(group))
    if len(group) == 0:
        return
    if len(group) == 1:
        emit_marker(group[0], output)
        return
    latitude = group[0]["Lat"]
    longitude = group[0]["Lon"]
    dist_group = group[0]["Dist_group"]
    icon = "icon{}".format(dist_group)
    count = len(group)
    city = group[0]["City"]
    title = "{} {}k permanents from {}".format(
        count, dist_group, city)
    desc = ""
    for record in group:
        desc += perm_in_group(record)
    js = (marker_group_template
          .format(latitude=latitude,
                  longitude=longitude,
                  count=count, 
                  icon=icon,
                  title=title, 
                  desc=desc))
    print(js, file=output)

marker_template_individual ="""
       var marker = L.marker([{latitude}, {longitude}],
           {{ 
              title: "{title}",
              alt: "{title}",
              icon: {icon},
              count: 1
           }}
            ).bindPopup("<div><p>{owner}</p>" +
                  "<p><a href={href}>{title}</a></p>" +
                  "<p>{dist}km</p>" + 
                  "<p>{notes}</p>" +
                  "</div>");
      markers.addLayer(marker);
"""

def emit_marker(record, output):
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

    js = (marker_template_individual
          .format(latitude=record["Lat"],
                  longitude=record["Lon"],
                  icon=icon,
                  title=html.escape(record["Perm_name"]),
                  owner=record["Perm_owner"],
                  dist=record["Perm_km"], 
                  href=record["Href"],
                  notes=record["Perm_notes"]))
    print(js, file=output)
                                
    
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
        accumulate(record, args.output)
        count += 1
        if args.limit and count >= args.limit:
            logger.info("Cutting off at {} permanents".format(count))
            break
    flush(args.output)
    copy_to_output("boilerplate/leaflet_postlog.html", args.output)


if __name__ == "__main__":
    main()


    
    
