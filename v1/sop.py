#-----------------------------------------------------------------------
# (C) Copyright RUSA, 2010
#
# sop.py
#
# The acronym "sop" is an homage to java's "system.out.println"
#
# Prints to the console with a nicely-formatted timestamp.
# logLevel 5 is most verbose.
# logLevel 0 is errors-only.
#-----------------------------------------------------------------------
import time

class Sop:
    def __init__(self, level):
        self.logLevel = level

    def setLogLevel(level):
        self.logLevel = level
        
    def getSopTimestamp(self):
        """Helper method returns a string with the current system timestamp 
        in a nice internationally-generic format: [YYYY-MMDD-HHMM-SS00]."""
        return time.strftime('[%Y-%m%d-%H%M-%S00]')

    def sop(self,level,methodname,message):
        """Helper method prints the specified method name and message 
        with a nicely formatted timestamp.
        (sop is an acronym for System.out.println() in java)"""
        if level <= self.logLevel:
            timestamp = self.getSopTimestamp()
            print "%s %s %s" % (timestamp, methodname, message)
