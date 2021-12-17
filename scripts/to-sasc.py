'''

convert ternary 0,1,? matrix with mutations on the rows to sasc format

'''

import sys

filename = sys.argv[1]
rows = []

lines = open(filename,'r')
m = len(lines.readline().split()) - 1

for line in lines :
    s, *row = line.split()

    row = [2 if x == '?' else x for x in row]
    assert len(row) == m

    rows.append(row)

for i in range(m) :
    print(*(row[i] for row in rows))
