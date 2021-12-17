'''

some useful functions used by several scripts

'''

# update column counts with a row
def update_counts(cs, row) :

    assert len(cs) == len(row)

    for i in range(len(cs)) :
        if row[i] == '1' :
            cs[i] += 1

    return cs


# pass a mask over a row
def mask_row(mask, row) :

    assert len(mask) == len(row)

    masked = []
    for x,y in zip(mask, row) :
        if x :
            masked.append(y)

    return masked


# process header info from a matrix
def process_header(filename) :

    lines = open(filename,'r')
    leg, *cells = lines.readline().split()
    assert leg == '#mutation\cell'

    m = len(cells)
    cs = m * [0]

    return cs, lines


# dump further processed header info from a matrix
def dump_header(filename, cs) :

    lines = open(filename,'r')
    leg, *cells = lines.readline().split()

    print(leg, *mask_row(cs, cells))

    return lines
