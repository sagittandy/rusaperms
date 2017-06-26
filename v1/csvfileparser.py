#-----------------------------------------------------------------------
# (C) Copyright RUSA, 2010
#
# csvfileparser.py
#
# Reads a generic CSV formatted file and parses its contents 
# according to the supplied 'schema' of column names.
# Writes new values to the CSV file.
#
# See unit test code at bottom for sample usage.
#-----------------------------------------------------------------------
import string
import sys
import time
from sop import Sop

# Logger.
mySop = Sop(3)
def sop(level,methodname,message):
    mySop.sop(level,"csvfileparser/" + methodname,message)

class CSVRecord:
    """Information from one line of a CSV formatted file.
    This object encapsulates a python dictionary, where
    the keys are the name of each CSV column, and
    values are the value of each CSV column.
    Args: listType="CSV": inputList must be one CSV string as read from a CSV file, and
                          columnNameList is a ordered list of strings with the name of each column.
          listType="LIST": inputList must be a python list of strings, and
                           columnNameList is a ordered list of strings with the name of each column.
          listType=None: inputList and columnNameList are ignored.  No values are stored."""
    def __init__(self,listType,inputList,columnNameList):
        """Initializes a CSVRecord, either from a string read from one line of a CSV file, 
        or from a list of strings containing elements.  Parses, and stores it.
        Parameter listType is either 'CSV' or 'LIST' """
        m = "CSVRecord/init:"
        sop(5,m,"Entry. listType=%s" % ( listType )) 
        if "CSV" == listType:
            self.initializeFromCSV(inputList,columnNameList)
        elif "LIST" == listType:
            self.initializeFromList(inputList,columnNameList) 
        elif None == listType:
            # Create an empty dictionary.
            self.recordDictionary = {}
        else:
            raise RuntimeError(m + " Error. Unexpected value for listType. listType=%s" % ( listType ))
        sop(5,m,"Exit.")

    def toString(self):
        rc = "CSVRecord/toString:\nnumRecords=%i" % ( len(self.recordDictionary) )
        for columnName in self.recordDictionary.keys():
            rc = rc + "\n  %s=%s" % ( columnName, self.recordDictionary[columnName] )
        return rc

    def initializeFromCSV(self,csvLine,columnNameList):
        """Initializes from a string read from one line of a CSV file, parses, and stores it."""
        m = "CSVRecord/initializeFromCSV:"
        sop(5,m,"Entry. csvLine=%s" % ( csvLine )) 

        # Escape!  Replace any commas within double-quoted strings with tildes.
        escapeChar = "~"
        if -1 != csvLine.find(escapeChar):
            raise RuntimeError("Program error: Can not use escape char '%s'. csvLine=%s" % ( escapeChar, csvLine ))

        i = 0
        escaped = False
        withinQuotes = False
        for letter in csvLine:
            if '"' == letter:
                if withinQuotes:
                    withinQuotes = False
                else:
                    withinQuotes = True
            elif "," == letter:
                if withinQuotes:
                    beforeComma = csvLine[:i]
                    afterComma = csvLine[1 + i:]
                    csvLine = beforeComma + escapeChar + afterComma
                    sop(9,m,"Escaping. i=%i beforeComma=>>>%s<<< afterComma=>>>%s<<< new csvLine=>>>%s<<<" % ( i, beforeComma, afterComma, csvLine ))
                    escaped = True
            i = i + 1
        if escaped:
            sop(9,m,"After escaping, csvLine=%s" % ( csvLine )) 

        # Convert the CSV line into a python list of strings.
        csvList = csvLine.split(",")

        # Undo the escape.
        if escaped:
            i = 0
            for column in csvList:
                csvList[i] = column.replace(escapeChar, ",")
                i = i + 1
            sop(5,m,"Un-did escape.")
            
        sop(5,m,"csvList=%s" % ( repr(csvList) ))
        if len(columnNameList) != len(csvList):
            print "csvList: ", csvList
            raise RuntimeError("Error. Unexpected number of elements in CSV line. expected=%i actual=%i" % ( len(columnNameList), len(csvList) ))
        self.recordDictionary = {}
        i = 0
        for columnName in columnNameList:
            self.recordDictionary[columnName] = csvList[i].strip()
            i = i + 1
        sop(5,m,"Exit. self.recordDictionary = %s" % ( repr(self.recordDictionary) ))

    def initializeFromList(self,recordList,columnNameList):
        """Initializes from a supplied list of element strings and stores it."""
        m = "CSVRecord/initializeFromList:"
        sop(5,m,"Entry. recordList=%s columnNameList=%s" % ( repr(recordList), repr(columnNameList) )) 

        # Bozo check.
        if len(columnNameList) != len(recordList):
            raise RuntimeError(
                "Error. Unexpected number of elements. len(recordList)=%i len(columnNameList)=%i"
                % ( len(recordList), len(columnNameList) ))

        # Store all values in the dictionary.
        self.recordDictionary = {}
        i = 0
        for columnName in columnNameList:
            self.recordDictionary[columnName] = recordList[i].strip('"').strip("'").strip()
            i = i + 1

        sop(5,m,"Exit. self.recordDictionary = %s" % ( repr(self.recordDictionary) ))

    def get(self,columnName):
        m = "CSVRecord/get:"
        sop(9,m,"Entry. columnName=%s" % ( columnName ))
        if columnName in self.recordDictionary.keys():
            sop(9,m,"Exit. Returning value from named column.")
            return self.recordDictionary[columnName]
        else:
            sop(9,m,"Exit. Returning None. Did not find columnName=%s." % ( columnName ))
            return None

    def put(self,columnName,columnValue):
        """Changes the value of an element in the dictionary.
        Raises an exception if the columnName does not exist."""
        m = "CSVRecord/put:"
        sop(9,m,"Entry. columnName=%s columnValue=%s" % ( columnName, columnValue ))
        if not columnName in self.recordDictionary.keys():
            raise RuntimeError( "Error. ColumnName does not exist in dictionary." % ( columnName ))
        else:
            self.recordDictionary[columnName] = columnValue
        sop(9,m,"Exit. set value %s to %s." % ( columnName,columnValue ))

    def appendValue(self,columnName,appendValue):
        """Appends to the value of an element in the dictionary.
        Handles the case where a value string is encapsulated with double-quotes.
        Raises an exception if the columnName does not exist."""
        m = "CSVRecord/appendValue:"
        sop(9,m,"Entry. columnName=%s appendValue=%s" % ( columnName, appendValue ))
        if not columnName in self.recordDictionary.keys():
            raise RuntimeError( "Error. ColumnName does not exist in dictionary." % ( columnName ))
        else:
            oldValue = self.recordDictionary[columnName]
            if oldValue.startswith('"') and oldValue.endswith('"'):
                newValue = '"' + oldValue.strip('"') + appendValue + '"'
            else:
                newValue = oldValue + appendValue
        self.recordDictionary[columnName] = newValue
        sop(5,m,"Exit. set column %s to new value %s." % ( columnName,newValue ))

    def cloneDeep(self):
        """Returns a new CSVRecord object with a deep clone of this object."""
        m = "CSVRecord/cloneDeep:"
        sop(9,m,"Entry.")

        # Create a new CSVRecord object.
        newCSVRecord = CSVRecord(None,None,None)

        # Copy all elements in the dictionary.
        for columnName in self.recordDictionary.keys():
            newCSVRecord.recordDictionary[ columnName ] = self.recordDictionary[ columnName ]

        sop(9,m,"Exit. Returning newCSVRecord %s" % ( newCSVRecord ))
        return newCSVRecord

class CSVFile:
    """Reads all information from one CSV formatted file."""
    def __init__(self,fileName,ignoreStringList,recordName,columnNameList):
        """fileName is the CSV file to be opened and parsed.
           ignoreStringList is a list of strings which should be ignored when parsing the file.
           recordName is the name of the column which will be used to index the dictionary herein.
           columnNameList is the name of the headings of all the columns in the CSV file."""
        m = "CSVFile/init:"
        sop(5,m,"Entry. fileName=%s ignoreStringList=%s recordName=%s columnNameList=%s" % ( fileName, repr(ignoreStringList),  recordName, repr(columnNameList) ))
        self.fileName = fileName
        self.ignoreStringList = ignoreStringList
        self.recordName = recordName
        self.columnNameList = columnNameList
        self.fileDictionary = {}

        # Open CSV file.
        sop(3,m,"Opening file read-only. %s" % ( fileName ))
        csvFile = open(fileName, 'r')  
        csvLines = csvFile.readlines()
        for csvLine in csvLines:
            csvLine = csvLine.strip()
            sop(5,m,"Next csvLine=%s" % ( csvLine ))

            # Ignore detritus.
            ignoreCsvLine = False
            for ignoreString in ignoreStringList:
                sop(9,m,"Considering ignoreString=%s" % ( ignoreString ))
                if csvLine.startswith(ignoreString):
                    sop(9,m,"csvLine starts with ignoreString. csvLine=%s ignoreString=%s" % ( csvLine, ignoreString))
                    ignoreCsvLine = True
                    break
            if ignoreCsvLine:
                sop(9,m,"Ignoring csvLine=%s" % ( csvLine ))
                continue

            # Create an object for the record.
            csvRecord = CSVRecord("CSV",csvLine,columnNameList)

            # Get the recordName value for this record.
            recordValue = csvRecord.get(recordName)

            # Save the record object.
            sop(5,m,"Saving record as %s" % ( recordValue ))
            self.fileDictionary[recordValue] = csvRecord

        # Close the CSV file.
        sop(3,m,"Closing file. %s" % ( fileName ))
        csvFile.close()

        # Remember success.
        self.initialized = "yes"


    def exists(self,recordName):
        """Indicates whether the named record exists."""
        return recordName in self.fileDictionary.keys()

    def getRecord(self,recordName):
        """Returns the requested record object or None."""
        m = "getRecord:"
        if recordName in self.fileDictionary.keys():
            sop(5,m,"Entry/Exit. Returning requested record. recordName=%s" % ( recordName ))
            return self.fileDictionary[recordName]
        else:
            sop(5,m,"Entry/Exit. Returning None. Did not find recordName=%s." % ( recordName ))
            return None

    def get(self,recordName,columnName):
        """Returns the value for one column of one line.
        Returns None if the record name does not exist.
        Fuzzy logic: Tries with and without double quotes around the recordName."""
        m = "CSVFile/get:"
        sop(5,m,"Entry. recordName=%s columnName=%s" % ( recordName, columnName ))
        if recordName in self.fileDictionary.keys():
            sop(5,m,"Exit. Returning value from named record.")
            return self.fileDictionary[recordName].get(columnName)
        elif recordName.strip('"') in self.fileDictionary.keys(): 
            sop(5,m,"Exit fuzzy. Returning value with double quotes removed.")
            return self.fileDictionary[recordName.strip('"')].get(columnName)
        elif '"' + recordName + '"' in self.fileDictionary.keys():  
            sop(5,m,"Exit fuzzy. Returning value with double quotes added.")
            return self.fileDictionary['"' + recordName + '"'].get(columnName)
        else:
            sop(5,m,"Exit. Returning None. Did not find recordName=%s." % ( recordName ))
            return None

    def getRecordNameKeys(self):
        """Returns a python list containing the record names of each element."""
        return self.fileDictionary.keys()

    def put(self, recordList):
        """Appends one record to the dictionary/database, and appends one line to the file.
        Warning: The caller must submit the records in the same sequence as columnNameList.
        TODO: Make this more robust in the future."""
        m = "CSVFile/put:"
        sop(5,m,"Entry. recordList=%s" % ( repr(recordList) ))

        # Verify the file has been read once, and internal variables are initialized.
        if "yes" != self.initialized:
            raise RuntimeError( m + " Error: File has not been read and internal variables initialized.")

        # Weak bozo check
        if len(recordList) != len(self.columnNameList):
            raise RuntimeError(m + " Error: Unexpected number of elements. len(recordList)=%i len(columnNameList)=%i" % ( len(recordList), len(columnNameList) ))

        # Create an object for the record.
        csvRecord = CSVRecord("LIST",recordList,self.columnNameList)

        # Get the recordName value for this record.
        recordValue = csvRecord.get(self.recordName)

        # Ensure the element is not already in the file and database.
        # Note: This is a weak mechanism to avoid duplicates in the file.  :-(
        if self.exists(recordValue):
            raise RuntimeError(m + " Error: Element already exists in database and file. recordValue=%s" % ( recordValue ))

        # Save the record object to the local dictionary.
        sop(5,m,"Saving record as %s" % ( recordValue ))
        self.fileDictionary[recordValue] = csvRecord

        # Now write the information to the file...

        # Convert the record list into one CSV string.
        recordString = ""
        for record in recordList:
            # Encapsulate in double-quotes if the record contains a comma.
            if -1 != record.find(',') and not record.startswith('"') and not record.endswith('"'):
                record = '"%s"' % ( record )
                sop(5,m,"Encapsulated record in double-quotes. record=%s" % ( record ))

            # Append with comma separator
            if 0 == len(recordString):
                recordString = record
            else:
                recordString = "%s,%s" % ( recordString, record )
            sop(5,m,"Appended. recordString=%s" % ( recordString ))

        # Bozo check.
        if 0 == len(recordString):
            raise RuntimeError( m + " Error. recordString is empty.")

        # End-of-line
        recordString = recordString + '\n'
        sop(5,m,"Converted. recordString=%s" % ( recordString ))

        # Open CSV file.
        sop(3,m,"Opening file in write-append mode. filename=%s" % ( self.fileName ))
        csvFile = open(self.fileName, 'a')  

        # Write.
        sop(3,m,"Writing string: %s" % ( recordString ))
        csvFile.write( recordString )

        # Done. Close the CSV file.
        sop(3,m,"Closing file. %s" % ( self.fileName ))
        csvFile.close()

        sop(5,m,"Exit. Wrote file.")

    def toString(self):
        m = "toString:"
        sop(5,m,"Entry.")
        sop(5,m,"self.fileName=%s" % ( self.fileName ))
        sop(5,m,"self.ignoreStringList=%s" % ( self.ignoreStringList ))
        sop(5,m,"self.recordName=%s" % ( self.recordName ))
        sop(5,m,"self.columnNameList=%s" % ( self.columnNameList ))
        sop(5,m,"self.fileDictionary=%s" % ( repr(self.fileDictionary) ))

#-----------------------------------------------------------------------
# main - unit test starts here.
#-----------------------------------------------------------------------
# m = "main:"
# sop(5,m,"Entry")
# 
# fileName = "/home/ding/tmp/permroutereport.city.state.csv"
# ignoreStringList = [ "/", "#", "Start Zipcode", "Route #", ]
# recordName = "Route Number"
# columnNameList = [ "Route Number", "Start City", "Start State" ]
# 
# csvFile = CSVFile(fileName,ignoreStringList,recordName,columnNameList)
# 
# # Test getting some elements.
# sop(5,m,"route 900: state=%s city=%s" % ( csvFile.get("900","Start State"), csvFile.get("900","Start City") ))
# 
# # Show all elements.
# recordNameKeys = csvFile.getRecordNameKeys()
# for recordName in recordNameKeys:
#     sop(5,m,"route %s: state=%s city=%s" % ( recordName, csvFile.get(recordName,"Start State"), csvFile.get(recordName,"Start City") ))
# 
# # Add new elements.
# csvFile.put( ["123", "456", '789'] )
# csvFile.put( ["bozo", '"th,ee"', 'cl,own'] )
# csvFile.put( ["ABC", "DEF", 'GHI'] )
# 
# recordNameKeys = csvFile.getRecordNameKeys()
# sop(5,m,"recordNameKeys=%s" % ( repr(recordNameKeys) ))
# sop(5,m,"Exit")
