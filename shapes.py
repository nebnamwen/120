import numpy
from geom import *
from math import *

def norm(v):
    return v / numpy.linalg.norm(v)

def prism(layer, key, pos, facecol, linecol, *rows):
    # draws a figure on a location with a main rotation axis (face or edge)
    # figure has the symmetry of a prism with a cross section depending on the location type
    # (triangle for an edge, pentagon for a face)
    #
    # display layer object
    # key (used to remove object from layer)
    # position (as a string)*
    #          * or pass a tuple (edge, vertex) or (face, cell) to draw only one side
    # face color (as a tuple of numbers)
    # line color (as a tuple of numbers)
    #
    # *rows:
    #    defines the shape to draw
    #    must be an odd number of total entries, each a tuple
    #    odd entries:
    #        defines a row of control points
    #        z - displacement of this row along the axis
    #        x - radius of points at the edge midpoints of the cross-sectional figure
    #        y - radius of points at the vertices of the cross-sectional figure
    #        parallel - whether or not to draw a horizontal line at this row
    #    even entries:
    #        defines a strip of faces between two consecutive rows of control points
    #        face - whether or not to draw a face at this row
    #               (or pass a tuple of unlike booleans to draw half the face)
    #        x meridian - whether or not to draw a vertical line at the edge midpoint
    #        y meridian - whether or not to draw a vertical line at the vertex
    #
    # radii of control points are relative to the base figure, so equal radii will draw a triangle or pentagon

    only = None
    if pos in faces or pos[0] in faces:
        if pos[0] in faces and pos[1] in cells:
            pos, only = pos
        coords = (faces, cells, edges, verts)
        links = (facecells, faceedges, edgeverts)
    elif pos in edges or pos[0] in edges:
        if pos[0] in edges and pos[1] in verts:
            pos, only = pos
        coords = (edges, verts, faces, cells)
        links = (edgeverts, edgefaces, facecells)

    P = coords[0][pos]
    for a in links[0][pos]:
        if only is None or a == only:
            A = coords[1][a] - P
            for b in links[1][pos]:
                B = coords[2][b] - P
                for c in links[2][b]:
                    C = coords[3][c] - P
                    for i in range(len(rows)):
                        if i % 2 == 0:
                            z, x, y, par = rows[i]
                            if par and linecol is not None:
                                layer.line(key, norm(P + z*A + x*B), norm(P + z*A + y*C), linecol)
                        else:
                            z0, x0, y0, _ = rows[i-1]
                            z1, x1, y1, _ = rows[i+1]

                            Vx0 = norm(P + z0*A + x0*B)
                            Vy0 = norm(P + z0*A + y0*C)
                            Vx1 = norm(P + z1*A + x1*B)
                            Vy1 = norm(P + z1*A + y1*C)

                            face, xmer, ymer = rows[i]

                            if face in (True, False): face = (face, face)

                            if face[0] and facecol is not None:
                                layer.triangle(key, Vx0, Vy0, Vx1, facecol)
                            if face[1] and facecol is not None:
                                layer.triangle(key, Vy1, Vy0, Vx1, facecol)
                            if xmer and linecol is not None:
                                layer.line(key, Vx0, Vx1, linecol)
                            if ymer and linecol is not None:
                                layer.line(key, Vy0, Vy1, linecol)

def pointfig(layer, key, pos, facecol, linecol, xyz, lines):
    # draws a figure on a location with regular polygonal symmetry
    # (dodecahedron for a cell, tetrahedron for a vertex)
    #
    # display layer object
    # key (used to remove object from layer)
    # position (as a string)*
    #          * or pass a tuple (edge, vertex) or (face, cell) to draw only one side
    # face color (as a tuple of numbers)
    # line color (as a tuple of numbers)
    #
    # xyz - radii of control points as a tuple
    #    x - face centers of the base figure
    #    y - edge midpoints of the base figure
    #    z - vertices of the base figure
    #
    # lines - which lines to draw as a tuple (xy, yz, xz)
    #
    # no separate parameter to skip drawing faces, pass None for face color instead
    #
    # radii of control points are relative to the base figure, so equal radii will draw a dodecahedron or tetrahedron

    if pos in cells:
        coords = (cells, faces, edges, verts)
        links = (cellfaces, faceedges, edgeverts)
    elif pos in verts:
        coords = (verts, edges, faces, cells)
        links = (vertedges, edgefaces, facecells)

    dx, dy, dz = xyz
    lxy, lyz, lxz = lines

    P = coords[0][pos]
    for x in links[0][pos]:
        X = coords[1][x] - P
        vX = norm(P + dx*X)
        for y in links[1][x]:
            Y = coords[2][y] - P
            vY = norm(P + dy*Y)
            for z in links[2][y]:
                Z = coords[3][z] - P
                vZ = norm(P + dz*Z)

                if facecol is not None:
                    layer.triangle(key, vX, vY, vZ, facecol)
                if lxy and linecol is not None:
                    layer.line(key, vX, vY, linecol)
                if lyz and linecol is not None:
                    layer.line(key, vY, vZ, linecol)
                if lxz and linecol is not None:
                    layer.line(key, vX, vZ, linecol)

def hexaprism(layer, key, pos, facecol, linecol, length, radius, subdiv=1):
    shape = []
    for i in range(subdiv):
        shape.extend([(length*i/subdiv,radius,radius/2,False), (True,True,True)])
    shape.extend([(length,radius,radius/2,True), (True,False,False), (length,0,0,False)])
    prism(layer, key, pos, facecol, linecol, *shape)

def pentaprism(layer, key, pos, facecol, linecol, length, radius, subdiv=1):
    shape = []
    for i in range(subdiv):
        shape.extend([(length*i/subdiv,radius,radius,False), (True,False,True)])
    shape.extend([(length,radius,radius,True), (True,False,False), (length,0,0,False)])
    prism(layer, key, pos, facecol, linecol, *shape)

def decaprism(layer, key, pos, facecol, linecol, length, radius, subdiv=1):
    ratio = faceedged / facevertd
    shape = []
    for i in range(subdiv):
        shape.extend([(length*i/subdiv,radius,radius*ratio,False), (True,True,True)])
    shape.extend([(length,radius,radius*ratio,True), (True,False,False), (length,0,0,False)])
    prism(layer, key, pos, facecol, linecol, *shape)

def facepolygon(layer, key, pos, facecol, linecol, radius):
    prism(layer, key, pos, facecol, linecol, (0,0,0,False), (True,False,False), (0,radius,radius,True))

def spheroid(layer, key, pos, facecol, linecol, length, radius):
    ratio = faceedged / facevertd
    rows = []
    for p in range(5):
        rows.extend([ (sin(p*pi/10)*length, radius*cos(p*pi/10), radius*ratio*cos(p*pi/10), False),
                      (True, p < 4, p < 4) ])
    rows.append((length,0,0,False))
    prism(layer, key, pos, facecol, linecol, *rows)

def dodecahedron(layer, key, pos, facecol, linecol, radius):
    pointfig(layer, key, pos, facecol, linecol, (radius,radius,radius), (False,True,False))

def icosahedron(layer, key, pos, facecol, linecol, radius):
    edgeratio = (cellfaced / celledged) ** 2
    vertratio = (cellfaced / cellvertd) ** 2
    pointfig(layer, key, pos, facecol, linecol, (radius,radius*edgeratio,radius*vertratio), (True,False,False))

def geodesic(layer, key, pos, facecol, linecol, radius):
    ratio = cellfaced / cellvertd
    pointfig(layer, key, pos, facecol, linecol, (radius,radius*ratio,radius*ratio), (False,True,True))

def rhombic30hedron(layer, key, pos, facecol, linecol, radius):
    raise NotImplementedError

def rhombic12hedron(layer, key, pos, facecol, linecol, radius):
    pointfig(layer, key, pos, facecol, linecol, (radius, radius/sqrt(3), radius/3), (True,True,False))

def dihedralspline(layer, key, pos, facecol, linecol, radius):
    f1, f2 = pos
    e = [ e for e in faceedges[f1] if e in faceedges[f2] ][0]
    v = verts[edgeverts[e][0]] - edges[e]
    c = cells[[ c for c in facecells[f1] if c in facecells[f2] ][0]]
    yradius = radius * edgevertd / cellfaced

    n = 10
    spine = [ norm((faces[f1] * (1 - x/n) + edges[e] * x/n) * (1 - x/n) +
                   (edges[e] * (1 - x/n) + faces[f2] * x/n) * x/n)
                   for x in range(n+1) ]
    tube = [ [ norm(p + v * radius * cos(t*pi/4) + (p - c) * yradius * sin(t*pi/4))
               for t in range(8) ] for p in spine ]

    for i in range(n):
        for j in range(8):
            if facecol is not None:
                layer.triangle(key, tube[i][j], tube[i][j-1], tube[i+1][j], facecol)
                layer.triangle(key, tube[i+1][j-1], tube[i][j-1], tube[i+1][j], facecol)
            if linecol is not None:
                layer.line(key, tube[i][j], tube[i+1][j], linecol)
