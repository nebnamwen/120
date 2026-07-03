import numpy
from collections import defaultdict
from itertools import permutations

__all__ = ['cells', 'cellcells',
           'faces', 'cellfaces', 'facecells',
           'edges', 'faceedges', 'edgefaces',
           'verts', 'edgeverts', 'vertedges']

cells = {}

for d in range(4):
    for v in (1,-1):
        c = numpy.array([0,0,0,0])
        c[d] = v
        cells["".join(["0Ii"[e] for e in c])] = c

for x in (-1,1):
    for y in (-1,1):
        for z in (-1,1):
            for w in (-1,1):
                cells["".join(["_Hh"[e] for e in (x,y,z,w)])] = numpy.array([x,y,z,w]) * 0.5

phi = (1 + 5 ** 0.5) / 2

phikeys = [ (phi / 2, "P", "p"),
            (0.5, "H", "h"),
            (0.5 / phi, "U", "u"),
            (0, "0") ]

def is_even_permutation(p):
    inversions = 0
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]:
                inversions += 1
    return inversions % 2 == 0
even_perms = [p for p in permutations(range(4)) if is_even_permutation(p)]

for p in (-1,1):
    for h in (-1,1):
        for u in (-1,1):
            phuz = (p,h,u,1)
            for perm in even_perms:
                cells["".join([phikeys[i][phuz[i]] for i in perm])] = numpy.array([phikeys[i][0]*phuz[i] for i in perm])

first = next(iter(cells))
adjacent = min([ numpy.linalg.norm(cells[c] - cells[first]) for c in cells if c is not first ])

cellcells = { c: [ c2 for c2 in cells if numpy.isclose(numpy.linalg.norm(cells[c] - cells[c2]), adjacent) ] for c in cells }

def sumkey(*l):
    return "".join(sorted(l))

def normsumvec(*l):
    v = numpy.sum([cells[c] for c in l], axis=0)
    return v / numpy.linalg.norm(v)

faces = { sumkey(c,c2): normsumvec(c,c2)
          for c in cells
          for c2 in cellcells[c] }

cellfaces = { c: [ sumkey(c, c2) for c2 in cellcells[c] ] for c in cells }

facecells = defaultdict(list)
for c, l in cellfaces.items():
    for f in l:
        facecells[f].append(c)

edges = { sumkey(c,c2,c3): normsumvec(c,c2,c3)
          for c in cells
          for c2 in cellcells[c]
          for c3 in cellcells[c] if c3 in cellcells[c2] }

faceedges = { sumkey(c,c2): [ sumkey(c,c2,c3)
                              for c3 in cellcells[c] if c3 in cellcells[c2] ]
              for c in cells
              for c2 in cellcells[c] }

edgefaces = defaultdict(list)
for f, l in faceedges.items():
    for e in l:
        edgefaces[e].append(f)

verts = { sumkey(c,c2,c3,c4): normsumvec(c,c2,c3,c4)
          for c in cells
          for c2 in cellcells[c]
          for c3 in cellcells[c] if c3 in cellcells[c2]
          for c4 in cellcells[c] if c4 in cellcells[c2] and c4 in cellcells[c3] }

edgeverts = { sumkey(c,c2,c3): [ sumkey(c,c2,c3,c4)
                                 for c4 in cellcells[c] if c4 in cellcells[c2]	and c4 in cellcells[c3] ]
              for c in cells
              for c2 in cellcells[c]
              for c3 in cellcells[c] if c3 in cellcells[c2] }

vertedges = defaultdict(list)
for e, l in edgeverts.items():
    for v in l:
        vertedges[v].append(e)
