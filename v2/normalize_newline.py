"""
Simple filter echoes input file with standard newline.
"""

import sys
fname = sys.argv[1]

infile = open(fname)
for line in infile:
    print( line.strip(), end="\n" )

