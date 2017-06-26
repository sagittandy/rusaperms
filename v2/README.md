#RUSA Perms Map Generator, V2

Create an interactive map of RUSA permanent start points from data extracted from the RUSA permanents database. 

Initial version was created by Andy Dingsor (sagittandy) using Python and Google Fusion Tables.  Version 2 is maintained by Michal Young (michal.young@gmail.com).  It borrows some code and lots of design from Andy's work, but has migrated the Python code from Python 2 to Python 3 and replaced Google Fusion Tables with the Leaflet.js framework for interactive maps.   

Many users are more familiar with Google maps than with Leaflet.js.  Conceptually they are very similar, although Leaflet is most often used with map data from Open Street Maps, processed and served by Mapbox.com.  I am using Leaflet because (a) the API is a little simpler and better documented, (b) some of the available plug-in components, and in particular the clustering plug-in, are much better than the corresponding components for Google Maps, and (c) while both Google Maps and Mapbox map data are free for light use, the pricing of Google Maps data rises very quickly when use exceeds the free threshold.  Mapbox also charges if usage exceeds a threshold, but there is much less chance of incurring a big bill. 

To use V2: 

Download CSV report of RUSA perms. You need a RUSA login for this.

* Sign-in here: http://www.rusa.org/login.html
* Go to Permanent Routes-> Report
* Enter the following search parameters:
    * Show permanent routes:   "Permanent Route Number"-> "is not a null field"
    * Show Fields:      
      * "Permanent route number",  
      * "Permanent route name", 
      * "Route owner Name, Surname",          
      *  "Start City",  
      *  "Start State",  
      *  "End City",  
      *  "End State", 
      *  "Through State(s)"           
      *  "Distance",  
      *  "Type",  
      *  "Reversible",  
      *  "Active?"       
      * "Output report as csv rather than HTML table"
  * Click "Generate Report"

  
Save the report in data/permroutereport.csv
Like this: 
![Image of form](https://github.com/sagittandy/rusaperms/blob/master/v2/graphics/RUSA_form.png?raw=true)

build.sh generates files in html folder; upload those files to whatever server you are using.

Currently hosting maps on Amazon S3, free tier: 
https://console.aws.amazon.com/s3/home?region=us-west-2