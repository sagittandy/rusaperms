# rusaperms
Generates online map of RUSA permanent starting locations

Initial version (in 'src' directory) used Google Fusion Tables and 
Python 2.x.  

v2 (from December 2016) uses leaflet.js.  

## To use v2 ##

Download CSV report of RUSA perms.  You need a RUSA login for this. 
* Sign-in here: http://www.rusa.org/login.html
* Go to Permanent Routes-> Report
* Enter the following search parameters:
    * Show permanent routes:   "Permanent Route Number"-> "is not a null field"
    * Show Fields:
        * "Permanent route number",  "Permanent route name", "Route owner Name, Surname", 
        *  Check all 5: "Start City",  "Start State",  "End City",  "End State", "Through State(s)"
            "Distance",  "Type",  "Reversible",  "Active?"
        * "Output report as csv rather than HTML table"
* Click "Generate Report"
* Save the report in data/permroutereport.csv 

build.sh generates files in html folder; upload those files to whatever 
server you are using. 
