import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GLU import *
from ctypes import *
from collections import defaultdict

VS = '''
void main ()
{
    vec4 position = gl_ModelViewMatrix * gl_Vertex;
    gl_Position = gl_ProjectionMatrix * vec4(position.xyz / (position.w + 1.0), 1.0);
    gl_FrontColor = gl_Color;
}
'''

FS = '''
void main()
{
    gl_FragColor = gl_Color;
}
'''

pygame.init()
display = (800,600)
pygame.display.set_mode (display, pygame.OPENGL|pygame.DOUBLEBUF, 24)
glViewport (0, 0, *display)

vertexShader = shaders.compileShader(VS, GL_VERTEX_SHADER)
fragmentShader = shaders.compileShader(FS, GL_FRAGMENT_SHADER)
shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)

glUseProgram(shaderProgram)

glEnableClientState (GL_VERTEX_ARRAY)
glEnableClientState (GL_COLOR_ARRAY)

glEnable(GL_DEPTH_TEST)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
# glTranslatef(0.0,0.0, -0.5)

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
    for v in edgeverts[e]:
        layers[0].line(verts[v], edges[e], numpy.array([1,1,1]))

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glRotatef(1, 3, 1, 1)

    for l in layers:
        l.draw()
    
    pygame.display.flip ()
    pygame.time.wait(10)

pygame.quit()
