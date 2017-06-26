"""
Generate html from CSV file of RUSA perms.

Experimental version --- using jinja2 to get some variability
in the boilerplate.

We assume the input CSV file is sorted by location and then distance.
The snarf step ensures sorting by location.  Documentation doesn't
say anything about sorting by distance, but this seems to be its behavior.
If this changes in the future, we may need to impose a sorting-and-bucketing
step. 
"""
import schemata
import jinja2
import configparser

import sys
import csv
import html 
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



def distance_group(record):
    """Rather than group exact distances, we'll group
       by distance class.
    """
    perm_dist = int((record["Perm_km"]).strip(" km"))
    next_bigger = "up"
    for distance in [1200, 1000, 600, 400, 300, 200, 100]:
        if perm_dist >= distance:
            return distance, next_bigger
        next_bigger = distance - 1
    return distance, next_bigger

# Control break logic --- we'll keep a list of records and
# produce a summary pin when location or distance bucket changes
group = [ ]
prior = [ ]

individual_markers = [ ]
grouped_markers = [ ]

def accumulate(record):
    """
    Control break logic:  Adds current record to
    the current group, after potentially dumping and
    restarting the current group.
    """
    global group
    global prior
    dist_group, next_bigger = distance_group(record)
    record["Dist_group"] = dist_group
    record["Next_bigger"] = next_bigger
    grouping = [ record["Lat"], record["Lon"], dist_group ]
    if grouping != prior:
        flush()
        prior = grouping
    group.append(record)

def flush():
    global group
    emit_group(group)
    group = [ ]


# def emit_group(group, output): 
#     logging.debug("Emitting group: {}".format(group))
#     if len(group) == 0:
#         return
#     if len(group) == 1:
#         emit_marker(group[0], output)
#         return
#     latitude = group[0]["Lat"]
#     longitude = group[0]["Lon"]
#     dist_group = group[0]["Dist_group"]
#     next_bigger = group[0]["Next_bigger"]
#     count = len(group)
#     city = group[0]["City"]
#     title = "{}  {}k-{}k permanents from {}".format(
#         count, dist_group, next_bigger, city)
#     desc = ""
#     for record in group:
#         desc += perm_in_group(record)
#     js = (marker_group_template
#           .format(latitude=latitude,
#                   longitude=longitude,
#                   count=count, 
#                   dist_group=dist_group,
#                   title=title, 
#                   desc=desc))
#     print(js, file=output)

def emit_group(group): 
    # Group is a list of records
    logging.debug("Emitting group: {}".format(group))
    if len(group) == 0:
        return
    if len(group) == 1:
        emit_marker(group[0])
        return
    marker_group = group[0].copy()
    marker_group["count"] = len(group)
    marker_group["perms"] = group.copy()
    grouped_markers.append(marker_group)

def emit_marker(record):
    """
    For convenience we take the record as a dict.
    """
    logging.debug("Formatting individual record {}".format(record))
    global individual_markers 
    marker = record.copy()
    # logging.debug("Emitting individual marker: {}".format(marker))
    individual_markers.append(marker)
    
def copy_to_output(path, output):
    """
    Copy the boilerplate files without change.
    Path is a string, output is an open file. 
    """
    with open(path, 'r') as input:
        for line in input:
            print(line, file=output, end="")

def init_templates( path="boilerplate" ):
    """
    Prepare to fill templates with Jinja2
    """
    global template_env
    template_loader = jinja2.FileSystemLoader(searchpath="boilerplate" )
    template_env = jinja2.Environment(
        loader=template_loader,
        lstrip_blocks=True
        )

def render_template( template_name, vars, output ):
    """
    Example render_template("template.hmtl", { "name": "foo" }, sys.stdout)
    """
    template = template_env.get_template( template_name )
    output_text = template.render( vars )
    print(output_text, file=output)


def config_options(config_file_path, version_group):
    """ 
    Loads up a dictionary with configuration options that we can use
    in Jinja2 template expansion
    """
    translations = { "True": True, "False": False,
                     "true": True, "false": False,
                     "yes": True, "no": False,
                     "Yes": True, "No": False }
    config = configparser.ConfigParser()
    config.read(config_file_path)
    group = config[version_group]
    env = { }
    for key in group:
        if group[key] in translations:
            logger.debug("Translating {}".format(key))
            env[key] = translations[group[key]]
        else:
            logger.debug("Not translating |{}|".format(key))
            env[key] = group[key]
    logger.debug("Environment: {}".format(env))
    return env


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
    parser.add_argument('--config',
                        help="Options group from leafletmaps.config", 
                        default="DEFAULT")
    args = parser.parse_args()
    env = config_options('leafletmaps.config', args.config)
    logger.info("Configuration options: {}".format(env))

    reader = csv.DictReader(args.input)
    init_templates()

    count = 0
    for record in reader:
        accumulate(record)
        count += 1
        if args.limit and count >= args.limit:
            logger.info("Cutting off at {} permanents".format(count))
            break
    flush()

    env["individual_markers"] = individual_markers
    env["grouped_markers"] = grouped_markers 
    render_template("leaflet_map.html", env, args.output)

if __name__ == "__main__":
    main()


    
    
