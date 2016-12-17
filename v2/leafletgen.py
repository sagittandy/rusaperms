"""
Generate html from CSV file of RUSA perms.

"""
import schemata
import sys
import csv
import html 
import logging
logging.basicConfig(level=logging.INFO)

# Boilerplate before and after the part we generate 
prolog="""<!DOCTYPE html>
<html>
<head>
	
	<title>RUSA Permanents</title>

	<meta charset="utf-8" />
	<meta name="viewport" content="width=device-width, initial-scale=1.0">

	<link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.2/dist/leaflet.css" />
	<script
	src="https://unpkg.com/leaflet@1.0.2/dist/leaflet.js"></script>

        <script src="lib/Leaflet.MakiMarkers.js"></script>

        <!-- Marker clustering -->
	<link rel="stylesheet"
        href="https://unpkg.com/leaflet.markercluster@1.0.0/dist//MarkerCluster.css" />
	<link rel="stylesheet"
        href="https://unpkg.com/leaflet.markercluster@1.0.0/dist//MarkerCluster.Default.css" />
	<script
        src="https://unpkg.com/leaflet.markercluster@1.0.0/dist//leaflet.markercluster-src.js">
        </script>
<style>
body {
    padding: 0;
    margin: 0;
}
html, body, #mapid {
    height: 100%;
}
.rider-icon { background-color: #00cc00;
               color: #ff0000;
               width: auto; }
         }
</style>
</head>
<body>




<div id="mapid"></div>
<script>

	var mymap = L.map('mapid').setView([37.7749, -122.4194], 5);

	L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1IjoibWljaGFseW91bmciLCJhIjoiY2l3c2xxY3gwMDA0NTJ1cXJsZW5yZDk5NSJ9.IWl2i9omf-ATaiGSNA7STw', {
		maxZoom: 18,
		attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, ' +
			'<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, ' +
			'Imagery © <a href="http://mapbox.com">Mapbox</a>',
		id: 'mapbox.streets'
	}).addTo(mymap);

       	var markers = L.markerClusterGroup();

        L.MakiMarkers.accessToken = "pk.eyJ1IjoibWljaGFseW91bmciLCJhIjoiY2l3c2xxY3gwMDA0NTJ1cXJsZW5yZDk5NSJ9.IWl2i9omf-ATaiGSNA7STw";


       var icon100 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#F0FF32",
                                         size: "m"});

       var icon200 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#8CD978",
                                         size: "m"});

       var icon300 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#64FEFF",
                                         size: "m"});

       var icon400 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#757EFF",
                                         size: "m"});

       var icon600 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#FD8F73",
                                         size: "m"});

       var icon1000 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#FC5655",
                                         size: "m"});

       var icon1200 = L.MakiMarkers.icon({icon: "bicycle",
                                         color: "#D930FF",
                                         size: "m"});

"""

postlog ="""
     mymap.addLayer(markers);
    
</script>
</body>
</html>
"""

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
    print(prolog, file=args.output)
    # sep = ""
    count = 0
    for record in reader:
        # print(sep, file=args.output)
        print(marker(record), file=args.output, end="")
        # sep=","
        count += 1
        if args.limit and count >= args.limit:
            logger.info("Cutting off at {} permanents".format(count))
            break
    print(postlog, file=args.output)

if __name__ == "__main__":
    main()


    
    
