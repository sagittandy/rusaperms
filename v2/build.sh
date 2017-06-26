#! /bin/sh 
# 
# Build the rusa perms and multi-state perms maps
# 
# 
# 
. env/bin/activate

# New: from downloaded report in CSV format
python3 convert_csv.py data/permroutereport.csv | python3 sort_csv.py - tmp/allperms.csv
python3 add_latlon.py tmp/allperms.csv tmp/everywhere.csv
python3 leafletgen.py tmp/everywhere.csv html/rusaperms.html --config all_perms

python3 select_multi.py tmp/everywhere.csv tmp/justmulti.csv
python3 leafletgen.py tmp/justmulti.csv html/rusa-multi.html --config multi_state

python3 select_minmax.py 50 199 tmp/everywhere.csv \
   | python3 leafletgen.py - html/permpops.html --config br100

python3 select_minmax.py 200 299 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms200.html --config br200

python3 select_minmax.py 300 399 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms300.html --config br300

python3 select_minmax.py 400 599 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms400.html --config br400

python3 select_minmax.py 600 999 tmp/everywhere.csv \
   | python3 leafletgen.py - html/perms600.html --config br600

python3 select_minmax.py 1000 5000 tmp/everywhere.csv \
   | python3 leafletgen.py - html/longperms.html --config long


#
#  Perms by state (smaller => faster loading on cell phones) 
# 

for state in AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY \
             LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NC ND NY \
             OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY \
             DC PR
do
  python3 select_state.py ${state} tmp/everywhere.csv - \
     | python3 leafletgen.py - html/${state}state.html --config ${state}
done
