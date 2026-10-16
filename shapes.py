import numpy
from geom import *
from math import *

def norm(v):
    return v / numpy.linalg.norm(v)

def prism(lyr, key, pos, facecol, linecol, *rows):
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
                                lyr.line(key, norm(P + z*A + x*B), norm(P + z*A + y*C), linecol)
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
                                lyr.triangle(key, Vx0, Vy0, Vx1, facecol)
                            if face[1] and facecol is not None:
                                lyr.triangle(key, Vy1, Vy0, Vx1, facecol)
                            if xmer and linecol is not None:
                                lyr.line(key, Vx0, Vx1, linecol)
                            if ymer and linecol is not None:
                                lyr.line(key, Vy0, Vy1, linecol)

def pointfig(lyr, key, pos, facecol, linecol, xyz, lines):
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
                    lyr.triangle(key, vX, vY, vZ, facecol)
                if lxy and linecol is not None:
                    lyr.line(key, vX, vY, linecol)
                if lyz and linecol is not None:
                    lyr.line(key, vY, vZ, linecol)
                if lxz and linecol is not None:
                    lyr.line(key, vX, vZ, linecol)

def hexaprism(lyr, key, pos, facecol, linecol, length, radius):
    prism(lyr, key, pos, facecol, linecol, (0,radius,radius/2,False), (True,True,True), (length,radius,radius/2,True), (True,False,False), (length,0,0,False))

def pentaprism(lyr, key, pos, facecol, linecol, length, radius):
    prism(lyr, key, pos, facecol, linecol, (0,radius,radius,False), (True,False,True), (length,radius,radius,True), (True,False,False), (length,0,0,False))

def decaprism(lyr, key, pos, facecol, linecol, length, radius):
    ratio = faceedged / facevertd
    prism(lyr, key, pos, facecol, linecol, (0,radius,radius*ratio,False), (True,True,True), (length,radius,radius*ratio,True), (True,False,False), (length,0,0,False))

def dodecahedron(lyr, key, pos, facecol, linecol, radius):
    pointfig(lyr, key, pos, facecol, linecol, (radius,radius,radius), (False,True,False))

def icosahedron(lyr, key, pos, facecol, linecol, radius):
    edgeratio = (cellfaced / celledged) ** 2
    vertratio = (cellfaced / cellvertd) ** 2
    pointfig(lyr, key, pos, facecol, linecol, (radius,radius*edgeratio,radius*vertratio), (True,False,False))

def rhombic30hedron(lyr, key, pos, facecol, linecol, radius):
    raise NotImplementedError

def rhombic12hedron(lyr, key, pos, facecol, linecol, radius):
    pointfig(lyr, key, pos, facecol, linecol, (radius, radius/sqrt(3), radius/3), (True,True,False))
