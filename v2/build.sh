#! /bin/sh 
# 
# Build the rusa perms and multi-state perms maps
# 
# 
# 
. env/bin/activate
# Old: scraping the web site html
# ./snarf.sh > tmp/raw.html
# python3 extract.py tmp/raw.html tmp/allperms.csv
# New: from downloaded report in CSV format
python3 convert_csv.py data/permroutereport.csv | python3 sort_csv.py - tmp/allperms.csv
python3 add_latlon.py tmp/allperms.csv tmp/everywhere.csv
python3 leafletgen.py tmp/everywhere.csv html/rusaperms.html

python3 select_multi.py tmp/everywhere.csv tmp/justmulti.csv
python3 leafletgen.py tmp/justmulti.csv html/rusa-multi.html
