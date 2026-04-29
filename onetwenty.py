import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GL.EXT.geometry_shader4 import *
from OpenGL.GLU import *
from ctypes import *
from collections import defaultdict
from itertools import permutations

VS = '''
#version 120

void main ()
{
    float PI = radians(180);
    float PI_2 = radians(90);
    vec4 position = gl_ModelViewMatrix * gl_Vertex;
    gl_Position = vec4(
        atan(position.x, position.z) / PI,
        tan(asin(position.y / length(position.xyz))) / PI_2,
        -asin(position.w) / PI_2,
        1.0
    );
    // gl_Position = gl_ProjectionMatrix * vec4(position.xyz / (position.w + 1.0), 1.0);
    gl_FrontColor = gl_Color * sqrt((position.w + 1.0) * 0.5);
}
'''

GS = '''
#version 120
#extension GL_EXT_geometry_shader : enable

void main() {
    float minx = gl_PositionIn[0].x;
    float maxx = gl_PositionIn[0].x;
    for(int i = 0; i < gl_VerticesIn; i++) {
        if (gl_PositionIn[i].x < minx) { minx = gl_PositionIn[i].x; }
        if (gl_PositionIn[i].x > maxx) { maxx = gl_PositionIn[i].x; }
    }

    if (maxx - minx <= 1.0) {
        for(int i = 0; i < gl_VerticesIn; i++) {
            gl_Position = gl_PositionIn[i];
            gl_FrontColor = gl_FrontColorIn[i];
            EmitVertex();
        }
        EndPrimitive();
    }
}
'''

FS = '''
#version 120

void main()
{
    gl_FragColor = gl_Color;
}
'''

pygame.init()

display = (1200,600)
pygame.display.set_mode (display, pygame.OPENGL|pygame.DOUBLEBUF, 24)
glViewport (0, 0, *display)

vertexShader = shaders.compileShader(VS, GL_VERTEX_SHADER)
geometryShader = shaders.compileShader(GS, GL_GEOMETRY_SHADER)
fragmentShader = shaders.compileShader(FS, GL_FRAGMENT_SHADER)

shaderProgram = glCreateProgram()
glAttachShader(shaderProgram, vertexShader)
glAttachShader(shaderProgram, geometryShader)
glAttachShader(shaderProgram, fragmentShader)

glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_INPUT_TYPE_EXT, GL_LINES)
glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_OUTPUT_TYPE_EXT, GL_LINE_STRIP)
glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_VERTICES_OUT_EXT, 2)

glLinkProgram(shaderProgram)
glUseProgram(shaderProgram)

glEnableClientState (GL_VERTEX_ARRAY)
glEnableClientState (GL_COLOR_ARRAY)

glEnable(GL_DEPTH_TEST)

# glMatrixMode(GL_PROJECTION)
# gluPerspective(60, (display[0]/display[1]), 0.1, 50.0)
# glMatrixMode(GL_MODELVIEW)

class layer():
    def __init__(self):
        self.triverts = []
        self.tricolors = []
        self.lineverts = []
        self.linecolors = []

        self.tridirty = False
        self.linedirty = False

        self.trivertbuf, self.tricolbuf, self.linevertbuf, self.linecolbuf = glGenBuffers(4)

    def triangle(self, a,b,c, color):
        self.tridirty = True

        for v in (a,b,c):
            self.triverts.append(v)
            self.tricolors.append(color)

    def line(self, a,b, color):
        self.linedirty = True

        for v in (a,b):
            self.lineverts.append(v)
            self.linecolors.append(color)

    @staticmethod
    def _bufferdata(b, l):
        glBindBuffer (GL_ARRAY_BUFFER, b)
        data = numpy.concatenate(l, dtype=numpy.float32)
        glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def draw(self):
        if self.tridirty:
            layer._bufferdata(self.trivertbuf, self.triverts)
            layer._bufferdata(self.tricolbuf, self.tricolors)
            self.tridirty = False

        if self.linedirty:
            layer._bufferdata(self.linevertbuf, self.lineverts)
            layer._bufferdata(self.linecolbuf, self.linecolors)
            self.linedirty = False

        # draw triangles
        glBindBuffer(GL_ARRAY_BUFFER, self.trivertbuf)
        glVertexPointer(4, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.tricolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)
    
        glDrawArrays (GL_TRIANGLES, 0, len(self.triverts))

        # draw lines
        glBindBuffer (GL_ARRAY_BUFFER, self.linevertbuf)
        glVertexPointer (4, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.linecolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)
    
        glDrawArrays (GL_LINES, 0, len(self.lineverts))

layers = [ layer() for i in range(1) ]

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

# print(cells)

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

for e in edges:
    layers[0].line(verts[edgeverts[e][0]], verts[edgeverts[e][1]], numpy.array([1,1,1]))

view_matrix = numpy.identity(4)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    transform = numpy.zeros((4,4))
    if keys[pygame.K_q]: transform[0][1] += 0.02
    if keys[pygame.K_e]: transform[0][1] -= 0.02
    if keys[pygame.K_LEFT]: transform[0][2] += 0.02
    if keys[pygame.K_RIGHT]: transform[0][2] -= 0.02
    if keys[pygame.K_UP]: transform[1][2] -= 0.02
    if keys[pygame.K_DOWN]: transform[1][2] += 0.02
    if keys[pygame.K_d]: transform[0][3] -= 0.01
    if keys[pygame.K_a]: transform[0][3] += 0.01
    if keys[pygame.K_LSHIFT]: transform[1][3] -= 0.01
    if keys[pygame.K_LCTRL]: transform[1][3] += 0.01
    if keys[pygame.K_w]: transform[2][3] -= 0.01
    if keys[pygame.K_s]: transform[2][3] += 0.01
    
    transform = numpy.identity(4) + transform - transform.T
    view_matrix, _ = numpy.linalg.qr(transform.dot(view_matrix))
    
    glLoadMatrixf(numpy.concatenate(view_matrix.T, dtype=numpy.float32))
    
    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    for l in layers:
        l.draw()
    
    pygame.display.flip ()
    pygame.time.wait(10)

pygame.quit()
