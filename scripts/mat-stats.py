'''

gather some descriptive statistics on a ternary matrix (fraction of
1s, etc.)

'''

import sys

# count the number of 1's and ?'s in a row
def count(row) :

    o = 0
    q = 0
    for c in row :

        if c == '1' :
            o += 1
        elif c == '?' :
            q += 1
        else :
            assert c == '0'

    return o, q

# Main
#----------------------------------------------------------------------

filename = sys.argv[1]

a = 0
b = 0
c = 0

s = filename.split('.')

if s[-2].startswith('b') :
    a, b, _ = s[-3:]
elif s[-2].startswith('c') :
    a, b, c, _ = s[-4:]
else :
    assert False

a = int(a.lstrip('a'))
b = int(b.lstrip('b'))
if c :
    c = int(c.lstrip('c'))

n = 0
m = 0
ones = 0
qs = 0
for line in open(filename, 'r') :

    if line.startswith('#') :
        m = len(line.split()) - 1
        continue

    s, *row = line.split()

    o, q = count(row)
    assert o + q

    n +=1
    ones += o
    qs += q

nm = n * m
fones = ones / float(nm) if n else 0
fqs = qs / float(nm) if n else 0
print(a, b, c, n, m, nm, ones, qs, fones, fqs, sep = ',')
