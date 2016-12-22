"""
Schemata of CSV files for mapping RUSA permanents.
"""

# As dumped from RUSA perms report screen (with the right options):
rusa_report = ["Route #", "Route name", "Owner Name", 
               "Start City", "Start State", "End City", "End State",
               "Within State(s)", "Distance", "Type", "Free-route?",
               "Reversible?", "Active?", "Super Randonn&eacute;e?",
               "Description" ]

# As produced by snarf.py:
rusa_snarf = ["State", "City", "Perm_km",  "Perm_id",
              "Perm_name",  "Perm_owner", "Perm_notes", "Perm_states" ]

# As decorated by add_latlon.py
geolocated = rusa_snarf + ["Lat", "Lon"]

# With further decoration, sorted into buckets
bucketed = geolocated.append("bucket")

# Location database (manual and from Google)
# Note place is City, State  (different from RUSA DB)
#
locations = [ "Place", "Lat", "Lon" ]
