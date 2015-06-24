#-----------------------------------------------------------------------
# (C) Copyright RUSA, 2010-2012
#
# rusa.perms.py
# 
# Generates two output files:
# - A KML file showing locations of RUSA permanents.
#   Content is organized using KML Folders in a heirarchy:
#    Folder with list of states
#        Folder with list of Cities
#            Permanents are listed in HTML format in each city Folder.
#
# - A CSV file for use with Google Fusion Tables.
#
# To use this program, the user must manually browse to the RUSA website 
# and generate a perm route report:
#   Search Parameters:
#       Permanent Route Number-> is not null
#   Show Fields:
#      "Permanent route number",
#      "Permanent route name",
#      "Start City",
#      "Start State",
#      "End City",
#      "End State",
#      Distance,
#      Type,
#      Reversible,
#      Active?
#   Format:  CSV
#
# Save the report in a file named permroutereport.csv, in
# the same directory as this program.
#
# To invoke this program:
#     python rusa.perms.py
#
# This program does the following:
#     - Reads permroutereport.csv and extracts information about each permanent.
#     - Determines latitude/longitude values for each permanent using
#           the Google Maps Geocoding API.
#     - Caches latitude/longitude values in file place.lat.lon.py
#           for future re-use.
#     - Generates two local files in the same directory as this program.
#           - rusaperms.kml for google maps
#           - rusaperms.csv for goole fusion tables
#
# To publish the results for consumer use with google maps:
#    - Transfer rusaperms.kml to a publicly-accessible webserver.
#    - Link the KML file to Google Maps using the following format:
#         <a href="http://maps.google.com/maps?q=http://my.web.site.com/rusaperms.kml">rusaperms.kml</a> 
#
# To publish the results for consumer use with Google Fusion Tables:
#     Update the file rusaperms.csv in Google Docs account, and recreate the map.
#
# Phew.
#-----------------------------------------------------------------------
import string
import sys
import time
from sop import Sop
from csvfileparser import CSVRecord, CSVFile
from getlatlon import GetLatLon

# Define False, True
(False,True)=(0,1)

# Logger.
mySop = Sop(3)
def sop(level,methodname,message):
    mySop.sop(level,"rusaperms/" + methodname,message)

class State:
    """Information about a state.
    # Contains a dictionary with keys=State Name
    Contains a list of CSVRecord objects which represent each perm.
    Corresponds to one KML file."""
    def __init__(self, name, longName):
        m = "State/init:"
        sop(5,m,"Entry. name=%s longName=%s" % ( name, longName )) 
        self.name = name            # 2-letter abbreviation, like GA.
        self.longName = longName    # Full state name, like Georgia.

        # This dictionary stores permanents with the same starting city and state.
        # Keys=location (ie, city, state).  
        # Values = List of CSVRecord/perm objects.
        self.permDictionary = {}

        sop(5,m,"Exit.")

    def getName(self):
        return self.name

    def toString(self):
        rc = "State: name=%s numLocations=%i" % ( self.getName(), len(self.permDictionary) )
        for cityStateName in self.permDictionary.keys():
            permCityStateList = self.permDictionary[ cityStateName ]
            rc = rc + "\n  cityStateName=%s numPerms=%i" % ( cityStateName, len(permCityStateList) )
        return rc

    def containsState(self, stateName):
        """Indicates whether this object houses the specified state name."""
        return stateName == self.name

    def addPermanent(self, permanent):
        """Adds the specified permanent to this state."""

        # Add the perm to the dictionary.
        permCityState = getPermCityState( permanent )
        if permCityState in self.permDictionary.keys():
            sop(5,m,"Found location in dictionary: %s" % ( permCityState ))
            permCityStateList = self.permDictionary[permCityState]
            permCityStateList.append( permanent )
        else:
            sop(5,m,"New location: %s" % ( permCityState ))
            permCityStateList = [ permanent ]
            self.permDictionary[ permCityState ] = permCityStateList

    def getDistanceColorForPermanent(self,perm):
        """Returns a different color name to be used in an HTML color string
        based upon the distance of the permanent.
        Pure eye candy."""
        m = "getDistanceColorForPermanent:"
        sop(5,m,"Entry.")
        distanceString = perm.get("Distance")
        distanceInt = int(distanceString)

        if distanceInt < 200:
            colorString = "black"
        elif distanceInt < 400:
            colorString = "green"
        elif distanceInt < 600:
            colorString = "blue"
        else:
            colorString = "red"

        sop(5,m,"Exit. Returning colorString=%s" % ( colorString ))
        return colorString

    def getPermCityStateListByDistance(self,permCityStateList):
        """Returns a list of perms sorted by distance, ascending."""
        m = "getPermCityStateListByDistance:"
        sop(5,m,"Entry. Num perms=%i" % ( len(permCityStateList) ))

        if 0 == len(permCityStateList):
            sop(5,m,"Exit. No perms.")
            return []

        # Create a dictionary where the keys are the distance and values are lists of perms.
        tmpDict = {}
        for perm in permCityStateList:
            distance = perm.get("Distance")
            sop(5,m,"distance=%s" % ( distance ))
            if distance in tmpDict:
                permList = tmpDict[distance]
                permList.append(perm)
            else:
                permList = [perm]
                tmpDict[distance] = permList
            sop(5,m,"tmpDict=%s" % ( repr(tmpDict) ))

        # Sort the dictionary by distance keys and extract the results to a new list.
        newList = []
        for key in sorted(tmpDict.iterkeys()):
            permList = tmpDict[key]
            sop(5,m,"key=%s permList=%s" % ( repr(key), repr(permList) ))
            for perm in permList:
                sop(5,m,"Appending perm=%s" % ( repr(perm) ))
                newList.append(perm)

        sop(5,m,"Exit. newList numPerms=%i" % ( len(newList) ))
        return newList
        
    def writeKMLFolder(self, kmlFile, placeLatLonDbase):
        """Appends the contents of this state to an open KML file in folder format."""
        m = "writeKMLFolder:"
        sop(3,m,"Entry. State=%s numCities=%s" % ( self.name, len(self.permDictionary.keys()) ))

        # Write nothing if this state has no permanents.
        if 0 == len(self.permDictionary.keys()):
            sop(5,m,"Exiting because this state has no permanents. state=%s" % ( self.name ))
            return

        # Initial text.
        kmlFile.write('    <Folder>\n' +
                      '      <name>' + self.name + " - " + self.longName + '</name>\n' +
                      '      <open>0</open>\n')

        # Get and sort (in alphabetical order) the list of city names.
        sortedPermDictionaryKeys = self.permDictionary.keys()
        sortedPermDictionaryKeys.sort()

        # Handle each city.
        for cityStateName in sortedPermDictionaryKeys:

            # Get the latitude and longitude for this permanent
            lat,lon = placeLatLonDbase.get( cityStateName )
            sop(5,m,"Got lat,lon.  lat=%s lon=%s" % ( lat, lon ))

            # Get the list of perms at this location.
            permCityStateList = self.permDictionary[ cityStateName ]

            # Get a sorted list based upon distance of the perm.
            sortedList = self.getPermCityStateListByDistance(permCityStateList)

            # Define a name string for the left column and viewable portion of link.
            nameString =  cityStateName
            # Really verbose...
            # for perm in permCityStateList:
            #     nameString = "%s, Route %s, %s" % ( nameString, perm.get("Route Number"), perm.get("Route Name") )

            # Define the description for the pop-up bubble in the placemark on the map.
            description = '        <description>\n'
            description = description + '          <![CDATA[\n            '
            firstPerm = True
            for perm in sortedList:  # permCityStateList:
                distanceColor = self.getDistanceColorForPermanent(perm)
                if firstPerm == True:
                    firstPerm = False
                else:
                    description = description + '<br>'

                # Description for each perm, eg: "200K Search for Black Creek"
                description = description + '<font color=\"%s\">%sK</font>' % ( distanceColor, perm.get("Distance") )
                description = description + ', <a href="http://www.rusa.org/cgi-bin/permview_GF.pl?permid=%s">%s</a>' % ( perm.get("Route Number"), perm.get("Route Name").strip('"') )

            # Disclaimer
            description = description + '<br><b>NOTICE:</b> Contact route owner for exact starting location.\n'
            description = description + '          ]]>\n'
            description = description + '        </description>\n'

            # Write the placemark to the KML file.
            kmlFile.write('      <Placemark>\n')
            kmlFile.write('        <name>%s</name>\n' % ( nameString ))
            kmlFile.write(description)
            # Note, coordinates is an ordered pair: longitude, latitude
            kmlFile.write('        <Point><coordinates>%s,%s</coordinates></Point>\n' % ( lon, lat ))
            kmlFile.write('      </Placemark>\n')
    
        # Ending text.
        kmlFile.write('    </Folder>\n')

        sop(5,m,"Exit.")

    def writeCSVFile(self, csvFile, placeLatLonDbase):
        """Appends the contents of this state to an open CSV file."""
        m = "writeCSVFile:"
        sop(3,m,"Entry. State=%s numCities=%s" % ( self.name, len(self.permDictionary.keys()) ))

        # Write nothing if this state has no permanents.
        if 0 == len(self.permDictionary.keys()):
            sop(5,m,"Exiting because this state has no permanents. state=%s" % ( self.name ))
            return

        # Get and sort (in alphabetical order) the list of city names.
        sortedPermDictionaryKeys = self.permDictionary.keys()
        sortedPermDictionaryKeys.sort()

        # Handle each city.
        for cityStateName in sortedPermDictionaryKeys:

            # Get the latitude and longitude for this permanent
            lat,lon = placeLatLonDbase.get( cityStateName )
            sop(5,m,"Got lat,lon.  lat=%s lon=%s" % ( lat, lon ))

            # Get the list of perms at this location.
            permCityStateList = self.permDictionary[ cityStateName ]

            # Write the city, latitude, and longitude to the CSV file on a new line.
            csvFile.write('%s,"%s",%s,%s,' % (mySop.getSopTimestamp(), cityStateName, lat, lon))

            # # Append information for each permanent to the line in one huge HTML string.
            # Note: I couldn't make this work in Google Fusion Tables. Apparently it will not accept html tags in a string.
            # firstPerm = True
            # for perm in permCityStateList:
            #
            #    # Start HTML list.
            #    if firstPerm == True:
            #        csvFile.write("<ul>")
            #        firstPerm = False
            #
            #    # Write distance, name, and URL.
            #    permDistance = perm.get("Distance")
            #    permName = perm.get("Route Name").replace('"','').replace(',','')
            #    permURL = "http://www.rusa.org/cgi-bin/permview_GF.pl?permid=%s" % ( perm.get("Route Number") )
            #    csvFile.write('<li>%sK <a href="%s" target="_blank" >%s</a>' % ( permDistance, permURL, permName ))
            #
            # # End HTML list
            # csvFile.write("</ul>,")

            # Write the number of permanents.
            csvFile.write("%s" % ( len(permCityStateList) ))

            # Get a sorted list based upon distance of the perm.
            sortedList = self.getPermCityStateListByDistance(permCityStateList)

            # Append information for each permanent to the line as three individual columns.
            for perm in sortedList:   # permCityStateList:
                # Write distance, name, and URL.
                permDistance = perm.get("Distance")
                permName = perm.get("Route Name").replace('"','').replace(',','')
                permURL = "http://www.rusa.org/cgi-bin/permview_GF.pl?permid=%s" % ( perm.get("Route Number") )
                permNum = perm.get("Route Number")
                csvFile.write(",%sK,%s,%s" % ( permDistance, permName, permNum ))

            # Close line.
            csvFile.write("\n")

        sop(5,m,"Exit.")

    def getMaxPermsPerCity(self):
        """Returns the number of perms and name of the city with the most perms."""
        m = "getMaxPermsPerCity:"
        sop(5,m,"Entry. State=%s numCities=%s" % ( self.name, len(self.permDictionary.keys()) ))

        # Exit if this state has no permanents.
        if 0 == len(self.permDictionary.keys()):
            sop(5,m,"Exiting because this state has no permanents. state=%s" % ( self.name ))
            return 0,""

        # Get the list of city names.
        permDictionaryKeys = self.permDictionary.keys()

        # Handle each city.
        maxPerms = 0
        maxCityName = ""
        for cityStateName in permDictionaryKeys:

            # Get the list of perms at this location.
            permCityStateList = self.permDictionary[ cityStateName ]

            if len(permCityStateList) > maxPerms:
                maxPerms = len(permCityStateList)
                maxCityName = cityStateName

        sop(5,m,"Exit. State=%s. Returning maxPerms=%i maxCityName=%s" % (self.name, maxPerms, maxCityName))
        return maxPerms, maxCityName

class States:
    """Contains a list of State objects."""
    def __init__(self):
        m = "States/init:"
        sop(5,m,"Entry.") 

        self.stateList = [
		   State("AL", "Alabama"),                      
           State("AK", "Alaska"), 
           State("AZ", "Arizona"), 
           State("AR", "Arkansas"),             
           State("BC", "British Columbia"),             
           State("CA", "California"),            
           State("CO", "Colorado"),                     
           State("CT", "Connecticut"),         
           State("DE", "Delaware"), 
           State("DC", "District of Columbia"),  
           State("FL", "Florida"),                      
           State("GA", "Georgia"),               
           State("HI", "Hawaii"),                 
           State("ID", "Idaho"),                   
           State("IL", "Illinois"),                 
           State("IN", "Indiana"),               
           State("IA", "Iowa"),                   
           State("KS", "Kansas"),                    
           State("KY", "Kentucky"),              
           State("LA", "Louisiana"),             
           State("ME", "Maine"),                
           State("MD", "Maryland"),                
           State("MA", "Massachusetts"),         
           State("MI", "Michigan"),        
           State("MN", "Minnesota"),                    
           State("MS", "Mississippi"),                  
           State("MO", "Missouri"),                     
           State("MT", "Montana"),               
           State("NE", "Nebraska"),                     
           State("NV", "Nevada"),                       
           State("NH", "New Hampshire"),                
           State("NJ", "New Jersey"),                   
           State("NM", "New Mexico"),                   
           State("NY", "New York"),                     
           State("NC", "North Carolina"),               
           State("ND", "North Dakota"),                 
           State("OH", "Ohio"),                         
           State("ON", "Ontario"),                         
           State("OK", "Oklahoma"),                  
           State("OR", "Oregon"),                       
           State("PA", "Pennsylvania"),                 
           State("PR", "Puerto Rico"),                  
           State("RI", "Rhode Island"),                 
           State("SC", "South Carolina"),               
           State("SD", "South Dakota"),                 
           State("TN", "Tennessee"),                    
           State("TX", "Texas"),                        
           State("UT", "Utah"),                         
           State("VT", "Vermont"),                      
           State("VA", "Virginia"),               
           State("WA", "Washington"),                   
           State("WV", "West Virginia"),                
           State("WI", "Wisconsin"),                    
           State("WY", "Wyoming"),                      
         ]

        sop(5,m,"Exit.")

    def getStates(self):
        """Returns list of state objects."""
        return self.stateList;


 
def getStateForPerm(stateList, stateName):
    """Returns one of the state objects based upon name."""
    m = "getStateForPerm:"
    sop(5,m,"Entry. stateName=%s" % ( stateName ))

    # Handle case where the report from RUSA does not include a state name.
    if 0 == len(stateName):
        raise "ERROR. stateName is empty."

    for state in stateList:
        if state.containsState(stateName):
            sop(5,m,"Exit. Returning state.")
            return state

    raise m + " Error: Could not find state for stateName=%s" ( stateName )

def getPermCityState(permRecord):
    """Returns a string with the 'location' of the perm.
    It is generated from the starting city and starting state.
    This important conversion is used in many places and thus 
    warrants its own commonized utility method.
    Input: a CSVRecord/permanent object.
    Output: a string"""
    m = "getPermCityState:"
    sop(9,m,"Entry.")

    permStartCity = permRecord.get("Start City")
    permStartState = permRecord.get("Start State")
    sop(9,m,"startCity=%s startState=%s" % ( permStartCity, permStartState ))

    permCityState = "%s, %s" % ( permStartCity.strip('"'), permStartState.strip('"') )
    sop(9,m,"Exit. Returning permCityState=%s" % ( permCityState ))
    return permCityState

def getMaxPermRouteNumber( permroutereport ):
    """Return the max perm route number for debug."""
    m = "getMaxPermRouteNumber:"
    sop(5,m,"Entry.")
    maxPermNumInt = -1

    permRecordNameKeys = permroutereport.getRecordNameKeys()
    for permRecordName in permRecordNameKeys:
        sop(5,m,"permRecordName=%s" % ( permRecordName ))

        # Get the CSVRecord object representing the permanent.
        permanent = permroutereport.getRecord(permRecordName)
        # sop(5,m,permanent.toString())

        # Skip inactive permanents.
        if "yes" != permanent.get("Active"):
            sop(5,m,"Skipping inactive permanent. permanent=%s" % ( permanent.toString() ))
            continue

        # Get the perm route number
        currentPermNumString = permanent.get("Route Number")
        currentPermNumInt = int(currentPermNumString)

        # Compare
        if currentPermNumInt > maxPermNumInt:
            maxPermNumInt = currentPermNumInt

    maxPermNumString = "%i" % ( maxPermNumInt )
    sop(5,m,"Exit.  Returning maxPermNumString=%s" % ( maxPermNumString ))
    return maxPermNumString


def writeKMLFile(stateList, placeLatLonDbase, maxPermRouteNumber):
    """Writes a single KML file for all perms.
    Uses the KML folder tag to expand/collapse the left panel."""
    m = "writeKMLFile:"
    filename = "rusaperms.kml"
    sop(5,m,"Entry. filename=%s maxPermRouteNumber=%s" % ( filename, maxPermRouteNumber ))

    # Open file.
    sop(3,m,"Opening file. filename=%s" % ( filename ))
    kmlFile = open(filename, 'w')  

    # Initial text.
    kmlFile.write('<?xml version="1.0" encoding="UTF-8"?>\n' +
                  '<kml xmlns="http://www.opengis.net/kml/2.2">\n' +
                  '<Document>\n' +
                  '  <Folder>\n' +
                  # Temporarily show the 'build date' of this KML file for debugging...
                  # '    <name>%s RUSA Permanents - Approximate Locations</name>\n' % ( mySop.getSopTimestamp() ))
                  '    <name>RUSA Permanents - Approximate Locations</name>\n')

    # Handle each state.
    for state in stateList:
        state.writeKMLFolder(kmlFile, placeLatLonDbase)

    # Ending text.  Include debug information (build date/timestamp, max perm number).
    kmlFile.write('  </Folder>\n' +
                  '  <Folder>\n' +
                  '    <name>%s %s</name>\n' % ( mySop.getSopTimestamp(), maxPermRouteNumber ) + 
                  '  </Folder>\n' +
                  '</Document>\n' + 
                  '</kml>')

    # Save file.
    sop(3,m,"Closing file. %s" % ( filename ))
    kmlFile.close()

    sop(5,m,"Exit.")


def getMaxPermsPerCity(stateList):
    """Returns the number of perms and name of the city with the most permanents."""
    m = "getMaxPermsPerCity:"

    maxPerms = 0
    maxCityName = ""
    for state in stateList:
        stateMax,stateCityNameMax = state.getMaxPermsPerCity()
        if stateMax > maxPerms:
            maxPerms = stateMax
            maxCityName = stateCityNameMax
    sop(5,m,"Exit. Returning maxPerms=%i maxCityName=%s" % ( maxPerms, maxCityName ))
    return maxPerms, maxCityName


def writeCSVFile(stateList, placeLatLonDbase, maxPermRouteNumber, maxPermsPerCity, filename):
    """Writes a single CSV file for all perms."""
    m = "writeCSVFile:"
    sop(5,m,"Entry. filename=%s maxPermRouteNumber=%s maxPermsPerCity=%i" % ( filename, maxPermRouteNumber, maxPermsPerCity ))

    # Open file.
    sop(5,m,"Opening file. filename=%s" % ( filename ))
    csvFile = open(filename, 'w')  

    # Initial header line.
    csvFile.write('tstamp,name,latitude,longitude,numperms')
    i = 0
    while (i < maxPermsPerCity): 
        iString = "%03i" % ( i )
        csvFile.write(",dist%s,name%s,num%s" % ( iString, iString, iString ))
        i = 1 + i
    csvFile.write("\n")

    # New attempt: All perms are written in one long HTML string in one column
    # csvFile.write('name,latitude,longitude,html\n')

    # Handle each state.
    for state in stateList:
        state.writeCSVFile(csvFile, placeLatLonDbase)

    # Save file.
    sop(5,m,"Closing file. %s" % ( filename ))
    csvFile.close()

    sop(5,m,"Exit.")


def sortPermsIntoStates(permroutereport, stateList, minStates):
    """Sorts permanents into states.  
    Stores results into State objects inside the stateList."""
    m = "sortPermsIntoStates:"
    sop(5,m,"Entry. minStates=%i" % ( minStates ))

    permRecordNameKeys = permroutereport.getRecordNameKeys()
    for permRecordName in permRecordNameKeys:
        sop(5,m,"permRecordName=%s" % ( permRecordName ))
    
        # Get the CSVRecord object representing the permanent.
        permanent = permroutereport.getRecord(permRecordName)
        # sop(5,m,permanent.toString())
    
        # Skip inactive permanents.
        if "yes" != permanent.get("Active"):
            sop(5,m,"Skipping inactive permanent. permanent=%s" % ( permanent.toString() ))
            continue
    
        # Skip permanents which do not cover enough states.
        coveredStatesString = permanent.get("Within State(s)")
        numCommas = coveredStatesString.count(",")
        numStates = 1 + numCommas
        if (numStates < minStates):
            sop(5,m,"Skipping permanent. numStates=%i" % ( numStates ))
            continue
        sop(5,m,"Accepting permanent. covered states: " + coveredStatesString)

        # Find the appropriate state and add the perm to the state. 
        state = getStateForPerm(stateList, permanent.get("Start State")) 
        sop(5,m,"Adding forward permanent %s to state %s." % ( permanent.get("Route Number"), state.getName() ))
        state.addPermanent(permanent)
    
        # Handle a reversible point-to-point permanent.
        if "Y" == permanent.get( "Reversible" ) and "PP" == permanent.get( "Type" ):
            if 0 < len( permanent.get( "End City" )) and 0 < len( permanent.get( "End State" )):
                # Duplicate the CSVRecord object.
                reversedPermanent = permanent.cloneDeep()
    
                # Reverse the Start and End values.
                reversedPermanent.put("Start State", permanent.get("End State"))
                reversedPermanent.put("Start City", permanent.get("End City"))
                reversedPermanent.put("End State", permanent.get("Start State"))
                reversedPermanent.put("End City", permanent.get("Start City"))
                sop(5,m,"origPerm=%s" % ( permanent.toString() ))
                sop(5,m,"revPerm=%s" % ( reversedPermanent.toString() ))
    
                # Add the string '(reversed)' to the perm name as an eyecatcher.
                reversedPermanent.appendValue("Route Name", " (Reversed)")

                # Find the appropriate state and add the permanent to the state.
                state = getStateForPerm(stateList, reversedPermanent.get("Start State") ) 
                sop(5,m,"Adding reversed permanent %s to state %s." % ( permanent.get("Route Number"), state.getName() ))
                state.addPermanent(reversedPermanent)
            else:
                errMsg = m + " WARNING. Reversible point-to-point permanent does not contain end city and end state. %s" % ( permanent.toString() )
                sop(0,m,errMsg)
                # raise errMsg

    sop(5,m,"Exit.")


#-----------------------------------------------------------------------
# main - the program starts here.
#-----------------------------------------------------------------------
m = "main:"
sop(3,m,"Entry")

sop(3,m,"Opening local place/latitude/longitude cache file.")
placeLatLonDbase = GetLatLon("place.lat.lon.csv")

sop(3,m,"Opening perm route report from the RUSA website.")
permFileName = "permroutereport.csv"
permIgnoreStringList = [ "/", "#", '"Place Name"', '"Route"', '"Route #"' ]
permColumnNameList = [ "Route Number","Route Name","Start City","Start State","End City","End State","Within State(s)","Distance","Type","Reversible","Active"]
permRecordName = permColumnNameList[0]
permroutereport = CSVFile(permFileName,permIgnoreStringList,permRecordName,permColumnNameList)

# Get the max perm route number for debug.
maxPermRouteNumber = getMaxPermRouteNumber( permroutereport )

#----------------------------------------------------
# Map all permanents.
#----------------------------------------------------
# Instantiate a new list of states.
statesObject = States()
stateList = statesObject.getStates()

sop(3,m,"Sorting perms into states. Including all permanents.")
minStates = 1
sortPermsIntoStates(permroutereport, stateList, minStates)

sop(3,m,"Create a KML file for Google Maps including all permanents.")
writeKMLFile(stateList, placeLatLonDbase, maxPermRouteNumber) 

sop(3,m,"Create a CSV file for Google Fusion Tables including all permanents.")
hardCodedMaxPermsPerCity = 50
filename = "rusaperms.csv"
writeCSVFile(stateList, placeLatLonDbase, maxPermRouteNumber, hardCodedMaxPermsPerCity, filename) 

#----------------------------------------------------
# Map permanents which cover more than one state.
#----------------------------------------------------
# Instantiate a new list of states.
statesObject = States()
stateList = statesObject.getStates()

sop(3,m,"Sorting perms into states. Including permanents which cover two or more states.")
minStates = 2
sortPermsIntoStates(permroutereport, stateList, minStates)

sop(3,m,"Create a CSV file for Google Fusion Tables including permanents covering more than one state.")
hardCodedMaxPermsPerCity = 50
filename = "rusaperms.multistate.csv"
writeCSVFile(stateList, placeLatLonDbase, maxPermRouteNumber, hardCodedMaxPermsPerCity, filename) 


# This is a hack.  Think of a better way.
# Alert the user if the actual number of columns has increased.
# If so, we must recreate a new CSV file in Google Docs, which gets a new URL link, which you must send to Mr Kuehn.
actualMaxPermsPerCity = 0
actualMaxCityName = ""
actualMaxPermsPerCity,actualMaxCityName = getMaxPermsPerCity(stateList)
sop(3,m,"MaxPermsPerCity: hardCoded=%i actual=%i city=%s" % ( hardCodedMaxPermsPerCity, actualMaxPermsPerCity, actualMaxCityName ))
if actualMaxPermsPerCity > hardCodedMaxPermsPerCity:
    sop(0,m,"\n========================================\n" +
            "ERROR, ERROR, ERROR...\n" +
            "The max perms per city has exceeded the number of columns in our spreadsheet.\n" +
            "Re-create the rusaperms.csv document in Google Docs.\n" + 
            "Create a new shortlink and send it to Mr Kuehn.\n" +
            "Also you may need to update gft_custom_info_windo.html.")

sop(3,m,"Exit")
