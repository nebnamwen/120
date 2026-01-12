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
    gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
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
glViewport (0, 0, 800, 600)

vertexShader = shaders.compileShader(VS, GL_VERTEX_SHADER)
fragmentShader = shaders.compileShader(FS, GL_FRAGMENT_SHADER)
shaderProgram = shaders.compileProgram(vertexShader, fragmentShader)

glEnableClientState (GL_VERTEX_ARRAY)
glEnableClientState (GL_COLOR_ARRAY)

glEnable(GL_DEPTH_TEST)
gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
glTranslatef(0.0,0.0, -5)

faces = []
for d in range(3):
    for v in (1,-1):
        f = numpy.array([0,0,0])
        f[d] = v
        faces.append(f)

adjacent = min([ numpy.linalg.norm(f - faces[0]) for f in faces if f is not faces[0] ])
        
facesforface = { tuple(f): [ f2 for f2 in faces if numpy.isclose(numpy.linalg.norm(f - f2), adjacent) ] for f in faces }
edgesforface = { tuple(f): [ f + f2 for f2 in facesforface[tuple(f)] ] for f in faces }

facesforedge = defaultdict(list)
for f in edgesforface:
    for e in edgesforface[f]:
        facesforedge[tuple(e)].append(numpy.array(f))

vertsforedge = { e: [ facesforedge[e][0] + facesforedge[e][1] + f3 for f3 in
                      [ f for f in facesforface[tuple(facesforedge[e][0])]
                        if tuple(f) in map(tuple, facesforface[tuple(facesforedge[e][1])]) ]
                     ] for e in facesforedge }

triverts = []
tricolors = []

lineverts = []
linecolors = []

for f in faces:
    for e in edgesforface[tuple(f)]:
        for v in vertsforedge[tuple(e)]:
            triverts.append(f)
            triverts.append(e)
            triverts.append(v)
            for i in range(3):
                tricolors.append(numpy.array([0,1,0]))

for e in vertsforedge:
    lineverts.append(vertsforedge[e][0])
    lineverts.append(vertsforedge[e][1])
    for i in range(2):
        linecolors.append(numpy.array([0,0,0]))

print(len(lineverts))
                
tvbo = glGenBuffers (1)
glBindBuffer (GL_ARRAY_BUFFER, tvbo)
data = numpy.concatenate(triverts, dtype=numpy.float32)
glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

tcbo = glGenBuffers (1)
glBindBuffer (GL_ARRAY_BUFFER, tcbo)
data = numpy.concatenate(tricolors, dtype=numpy.float32)
glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

lvbo = glGenBuffers (1)
glBindBuffer (GL_ARRAY_BUFFER, lvbo)
data = numpy.concatenate(lineverts, dtype=numpy.float32)
glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

lcbo = glGenBuffers (1)
glBindBuffer (GL_ARRAY_BUFFER, lcbo)
data = numpy.concatenate(linecolors, dtype=numpy.float32)
glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

glUseProgram(shaderProgram)

running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glRotatef(1, 3, 1, 1)

    glBindBuffer (GL_ARRAY_BUFFER, tvbo)
    glVertexPointer (3, GL_FLOAT, 0, None)

    glBindBuffer (GL_ARRAY_BUFFER, tcbo)
    glColorPointer (3, GL_FLOAT, 0, None)
    
    glDrawArrays (GL_TRIANGLES, 0, 144)

    glBindBuffer (GL_ARRAY_BUFFER, lvbo)
    glVertexPointer (3, GL_FLOAT, 0, None)

    glBindBuffer (GL_ARRAY_BUFFER, lcbo)
    glColorPointer (3, GL_FLOAT, 0, None)
    
    glDrawArrays (GL_LINES, 0, 24)

    pygame.display.flip ()
    pygame.time.wait(10)

pygame.quit()
