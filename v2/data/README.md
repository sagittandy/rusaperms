# RUSA perms map / data  # 

## What's here ##

### Versioned in git ###

* latlon_auto.csv:  This is a cache of the geocoding results
  from the geocoding service (currently Google Maps).  When we 
  geocode a location from the RUSA perms database, we first consult
  the cache to see if we already know the location. We use the 
  cached lat-lon values if present.  On a cache miss, we consult 
  the geocoding service and update the cache.  This file will be 
  updated on each run of the pipeline.  (It should be updated only 
  when there have been additions, but currently it is re-written 
  on each run.)

* latlon_manual.csv:  These are 'exceptions' --- entries that we 
  don't trust the geocoding service for.  This can happen for several 
  reasons.  Our geocoding service may simply return the wrong answer 
  (which we learn about when a perm owner reports that their perm is 
  showing up in Nova Scotia but should be in California), or the location 
  might not be known to the geocoding service (like "SH 160 at NC/SC
  state line, NC"), or the perms database entry might have a
  misspelling  ("Wilsons Corner, TX").  Unlike latlon_auto.csv, this 
  file is edited manually, usually with Excel.  Entries in
  latlon_manual.csv take precedence over entries in latlon_auto.csv,
  but it is less confusing if the two files do not have entries in
  common. 

### Not versioned in git ###

* permroutereport.csv:  This file is taken from the RUSA web site. 
  It is not versioned because we should always work with a fresh
  copy. Log in to the RUSA site (https://rusa.org/login), choose 
  "Permanent Routes " >> "report", and under "Show Fields" select
      * permanent route number  
      * permanent route name    
      * route owner name (firstname surname)  
      * start city, start state, end city, end state 
      * distance, type, free-route?, revisible, active
      * Super Randonnee?
      * Output report as csv rather than HTML table
 
  Our system will generally work ok if extra fields are included in
  the report, but should report errors if a field is missing 


   