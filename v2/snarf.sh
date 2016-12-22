#! /bin/bash
#
# OBSOLETE --- screen-scraping didn't give me all the data I needed. 
# Now using CSV report and convert_csv.py.  See howto-snarf.rtf
#
# Suck down RUSA perms table with curl
# for further processing with other scripts. 
# 
# Writes to standard output. 
# 

curl -k "https://rusa.org/cgi-bin/permsearch_PF.pl" \
   -d   dist="" -d free="" -d type="" -d through=""  \
   -d owner="" -d sortfield=location -d shwall=""   \
   -d submit=search
