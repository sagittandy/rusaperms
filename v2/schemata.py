"""
Schemata of CSV files for mapping RUSA permanents.
"""

# As produced by snarf.py:
rusa_snarf = ["State", "City", "Perm_km", "Perm_climb", "Href",
              "Perm_name",  "Perm_owner", "Perm_notes" ]

# As decorated by add_latlon.py
geolocated = rusa_snarf + ["Lat", "Lon"]

# Location database (manual and from Google)
# Note place is City, State  (different from RUSA DB)
#
locations = [ "Place", "Lat", "Lon" ]
