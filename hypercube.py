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
    gl_Position = gl_ProjectionMatrix * vec4(position.xyz / (position.w + 3.0), 1.0);
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
glTranslatef(0.0,0.0, -0.5)

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
        
for x in (1, -1):
    for y in (1, -1):
        for z in (1, -1):
            for w in (1, -1):
                v = numpy.array([x,y,z,w])
                for d in range(4):
                    e = [x,y,z,w]
                    e[d] = 0
                    layers[0].line(v, numpy.array(e), numpy.array([1,1,1]))

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
