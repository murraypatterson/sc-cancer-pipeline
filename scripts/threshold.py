'''

keep only those rows from a ternary matrix with more than c 1s for a
given threshold c.  Discard any column with no 1s

'''

import sys
from functions import *

# count the number of 1s in a row
def count(cs) :

    a = 0
    for c in cs :
        if c == '1' :
            a += 1

    return a


# Main
#----------------------------------------------------------------------

filename = sys.argv[1]
c = int(sys.argv[2])

# first pass
cs, lines = process_header(filename)
for line in lines :
    s, *row = line.split()

    if count(row) < c :
        continue

    cs = update_counts(cs, row)

# second pass
lines = dump_header(filename, cs)
for line in lines :
    s, *row = line.split()

    if count(row) < c :
        continue

    print(s, *mask_row(cs, row))
