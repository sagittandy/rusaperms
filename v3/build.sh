#! /bin/bash
#
# Build files in the html directory
#
# Step 1: Clear and back up
mv -f html/*.html bak

# Build for each state or region
for state in AL AK AZ AR CA CO CT DE FL GA HI ID IL IN IA KS KY \
             LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NC ND NY \
             OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY \
             DC PR
do
  echo "Pulling data for ${state}"
  python3 pull_data.py ${state}
  echo "Building map for ${state}"
  python3 leafletgen.py data/${state}.csv html/${state}.html --config ${state}
  echo
done

echo "Building index"
python3 indexgen.py --output html/index.html
