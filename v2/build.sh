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

python3 select_minmax.py 50 199 tmp/everywhere.csv \
   | python3 leafletgen.py - html/permpops.html

python3 select_minmax.py 200 299 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms200.html

python3 select_minmax.py 300 399 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms300.html

python3 select_minmax.py 400 599 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms400.html

python3 select_minmax.py 600 999 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms600.html

python3 select_minmax.py 1000 5000 tmp/everywhere.csv \
   | python3 leafletgen.py - html/longperms.html
