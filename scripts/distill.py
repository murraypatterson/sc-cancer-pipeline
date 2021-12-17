description = '''

Given a (phased) variant read counts file and a mapping from cell to
clone, filter out the cells from certain clones, and then filter out
the mutations from cells which appear in certain (other) clones, and
convert what remains into a matrix format M(i,j) = number of reads for
SNV i in cell j (from both haplotypes cumulatively).

Note: that it is assumed that the read counts file is sorted (by
chromosome and position), and that in the mapping the clones which are
not "None" have a cluster number which is the same as the numerical
part of the cluster name.

'''

import sys
import argparse

# build dictionary from cell to clone mapping (filtering certain ones)
def cell_to_clone(lines, to_filter) :

    clone = {}
    for line in lines :

        if line.startswith('#') :
            continue

        cell, cluster, clone_name = line.split()
        if clone_name in to_filter :
            continue

        clone[cell] = cluster

    return clone

# True if none of the cells are of clone given_clones else False
def not_of_clones(given_clones, cells, clone) :

    for cell in cells :
        if cells[cell] and clone[cell] in given_clones :
            return False

    return True

# dump a row of the matrix based on a set of cells wrt a reference set
def dump_row(ref, cells) :

    out = []
    for cell in ref :
        out.append(cells[cell] if cell in cells else 0)

    return out

#
# Parser
#----------------------------------------------------------------------

parser = argparse.ArgumentParser(description = description)

parser.add_argument(
    '-f', '--clones', metavar = 'mapping.tsv',
    help = 'file with mapping from cell to clone')
parser.add_argument(
    '-c', '--cells', nargs = '+',
    help = 'clones from which to filter cells')
parser.add_argument(
    '-m', '--mutations', nargs = '+',
    help = 'clones from which to filter mutations')

args = parser.parse_args()

print('file with mapping from cell to clone:', args.clones, file = sys.stderr)
print('filtering cells from clones:', *(args.cells), file = sys.stderr)
print('filtering mutations from clones:', *(args.mutations), file = sys.stderr)

# Main
#----------------------------------------------------------------------

clone = cell_to_clone(open(args.clones,'r'), args.cells)
ref = list(x for x in clone)

current = '' # current mutation (defined by chr:pos, which is sorted)
cells = {} # variant read counts of cells of current mutation

print('#mutation\cell', *ref)
for line in sys.stdin :
    ch, pos, cell, h1, h2 = line.split()

    mut = '{}:{}'.format(ch, pos)
    if mut != current :

        if cells and not_of_clones(args.mutations, cells, clone) and len(cells) < len(ref) :
            print(current, *dump_row(ref, cells))

        current = mut
        cells = {}

    if cell in ref :
        cells[cell] = int(h1) + int(h2)
