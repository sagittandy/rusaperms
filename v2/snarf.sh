#! /bin/bash
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
