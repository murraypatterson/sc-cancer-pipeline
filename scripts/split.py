'''

split columns of a ternary matrix into submatrices according to clones
given a mapping from cell to clone.  Discard any row with no 1s

'''

import sys
import os
from collections import defaultdict
from functions import *

lines = open(sys.argv[1],'r')
mapping = cell_to_clone(open(sys.argv[2],'r'))

leg, *cells = lines.readline().split()
assert leg == '#mutation\cell'
m = len(cells)

clone = {} # cell (column) index to clone
for i in range(m) :
    clone[i] = mapping[cells[i]]
clones = set(clone.values())

filename, ext = os.path.splitext(sys.argv[1])
assert ext == '.mat'

# open file for each clone, and partition header into each
row = defaultdict(list)
for i in range(m) :
    row[clone[i]].append(cells[i])

handle = {}
for c in clones :
    handle[c] = open('{}.clone{}{}'.format(filename,c,ext),'w')    
    print(leg, *row[c], file = handle[c])

# now partition the rows into each file
for line in lines :
    s, *r = line.split()

    row = defaultdict(list)
    for i in range(m) :
        row[clone[i]].append(r[i])

    for c in clones :
        if no_ones(row[c]) :
            continue
        
        print(s, *row[c], file = handle[c])

# close each file
for c in clones :
    handle[c].close()
