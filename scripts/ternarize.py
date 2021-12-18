'''

apply a pair (a,b), a < b, of thresholds to a matrix from
distill-snvs, setting: (1) values < a to 0; (2) values >= a, < b to ?;
and (3) values >= b to 1, effectively converting to a ternary matrix.
Discard any row or column with no 1s

'''

import sys
from functions import *

# apply (a,b) thresholding scheme to a row
def apply_ab(row, a, b) :

    ts = []
    for c in row :
        t = '1'

        if int(c) < a :
            t = '0'
        elif int(c) < b :
            t = '?'

        ts.append(t)

    return ts


# Main
#----------------------------------------------------------------------

filename = sys.argv[1]
a = int(sys.argv[2])
b = int(sys.argv[3])

# first pass
cs, lines = process_header(filename)
for line in lines :

    s, *row = line.split()
    row = apply_ab(row, a, b)
    cs = update_counts(cs, row)

# second pass
lines = dump_header(filename, cs)
for line in lines :

    s, *row = line.split()
    row = apply_ab(row, a, b)

    # discard any row with no 1s
    if no_ones(row) :
        continue

    print(s, *mask_row(cs, row))
