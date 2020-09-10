# RUSA perms map, version 3

Now that all active perms have a 
RWGPS link in the database, we 
can do better. 

* Pull URLs and names from RUSA: 
  query_rusa_perms.py
  
* Determine which have changed; 
  See [`https://github.com/willvousden/rwgps-sync`](https://github.com/willvousden/rwgps-sync)
  (Maybe ... )
  
* Pull and filter routes that have
  changed. 
  
  Initial plan, data schemata: 
  * From RUSA database, create CSV for each 
    state with route#, name, link
  * From RWGPS, create a file per route, named 
    route_9999.csv, with (lat, lon, dist)
  * Also controls_9999.cvs, with (lat, lon, dist, desc)