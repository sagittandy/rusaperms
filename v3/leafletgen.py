"""
Generate html from CSV file of RUSA perms.

Currently drawing from UNSORTED CSV file and not grouping
routes.
FIXME: Sort and group using minimum distance (200 meters?)
       Will need method for linking route details.
"""
import jinja2
import configparser

import sys
import csv
import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


def distance_group(record):
    """Rather than group exact distances, we'll group
       by distance class.
    """
    perm_dist = int(record["dist"])
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
    grouping = [ record["lat"], record["lon"], dist_group ]
    if grouping != prior:
        flush()
        prior = grouping
    group.append(record)

def flush():
    global group
    emit_group(group)
    group = [ ]


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

def init_templates( path="templates" ):
    """
    Prepare to fill templates with Jinja2
    """
    global template_env
    template_loader = jinja2.FileSystemLoader(searchpath=path)
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
            log.debug("Translating {}".format(key))
            env[key] = translations[group[key]]
        else:
            log.debug("Not translating |{}|".format(key))
            env[key] = group[key]
    log.debug("Environment: {}".format(env))
    return env

def append_points(record: dict):
    """For each route nnnn, there should be a file
    data/points/nnnn.points that is a (json) list of
    lat, lon pairs.
    """
    pid = record["pid"]
    with open(f"data/points/{pid}.json") as f:
        points = f.readline()
    record["points"] = points

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Generate html from geocoded perms")
    parser.add_argument('input', help="CSV from RUSA with lat,lon added",
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
    log.debug("Configuration options: {}".format(env))

    reader = csv.DictReader(args.input)
    init_templates()

    count = 0
    for record in reader:
        # Reject records that do not have a valid lat, lon
        if not record["lat"]:
            log.warning(f"Skipping {record['pid']} {record['name']}; no location")
            continue
        append_points(record)
        accumulate(record)
        count += 1
        if args.limit and count >= args.limit:
            log.info("Cutting off at {} permanents".format(count))
            break
    flush()

    env["individual_markers"] = individual_markers
    env["grouped_markers"] = grouped_markers ## NOT IN USE!
    env["sidebar"] = True;
    render_template("leaflet_map.html.jinja2", env, args.output)
    log.info("{} perms generated on {}".format(count, args.output.name))

if __name__ == "__main__":
    main()


    
    
