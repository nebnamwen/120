import pygame
import numpy
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GL.EXT.geometry_shader4 import *
# from OpenGL.GLU import *
from ctypes import *
from collections import defaultdict

vertShader_mercator = '''
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
    vec4 fog_color = vec4 __BACKGROUND_COLOR__;
    float fade = sqrt((position.w + 1.0) * 0.5);
    gl_FrontColor = mix(fog_color, gl_Color, fade);
}
'''

geomShader_mercator = '''
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

fragShader_passthrough = '''
#version 120

void main()
{
    gl_FragColor = gl_Color;
}
'''

LINES = (GL_LINES, GL_LINE_STRIP, 2)
TRIANGLES = (GL_TRIANGLES, GL_TRIANGLE_STRIP, 3)

class display:
    def __init__(self, bg_color):
        bg_color_alpha = bg_color + (1.0,)
        bg_color_string = str(bg_color_alpha)

        pygame.init()
        viewport = (1200,600)
        pygame.display.set_mode (viewport, pygame.OPENGL|pygame.DOUBLEBUF, 24)
        glViewport (0, 0, *viewport)

        glClearColor(*bg_color_alpha)

        mercatorProgram = ( shaders.compileShader(vertShader_mercator.replace('__BACKGROUND_COLOR__', bg_color_string), GL_VERTEX_SHADER),
                            shaders.compileShader(geomShader_mercator, GL_GEOMETRY_SHADER),
                            shaders.compileShader(fragShader_passthrough, GL_FRAGMENT_SHADER) )

        _lineProgram = self.shaderProgramForType(mercatorProgram, *LINES)
        _triProgram = self.shaderProgramForType(mercatorProgram, *TRIANGLES)

        self.layers = [ layer(_lineProgram, _triProgram) for i in range(1) ]

        glEnableClientState (GL_VERTEX_ARRAY)
        glEnableClientState (GL_COLOR_ARRAY)

        glEnable(GL_DEPTH_TEST)

        self.view_matrix = numpy.identity(4)

    @staticmethod
    def shaderProgramForType(compiledShaders, input_t, output_t, verts):
        shaderProgram = glCreateProgram()

        for s in compiledShaders:
            glAttachShader(shaderProgram, s)

        glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_INPUT_TYPE_EXT, input_t)
        glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_OUTPUT_TYPE_EXT, output_t)
        glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_VERTICES_OUT_EXT, verts)

        glLinkProgram(shaderProgram)
        return shaderProgram

    def update(self):
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
        new_view_matrix, _ = numpy.linalg.qr(transform.dot(self.view_matrix))

        for i in range(4):
            if new_view_matrix[:, i].dot(self.view_matrix[:, i]) < 0:
                new_view_matrix[:, i] *= -1

        self.view_matrix = new_view_matrix
    
        glLoadMatrixf(numpy.concatenate(self.view_matrix.T, dtype=numpy.float32))
    
        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for l in self.layers:
            l.draw()
    
        pygame.display.flip ()
        pygame.time.wait(10)

    def quit(self):
        pygame.quit()

class layer():
    def __init__(self, lineProgram, triProgram):
        self.lineProgram = lineProgram
        self.triProgram = triProgram
        
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
        glUseProgram(self.triProgram)

        glBindBuffer(GL_ARRAY_BUFFER, self.trivertbuf)
        glVertexPointer(4, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.tricolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)
    
        glDrawArrays (GL_TRIANGLES, 0, len(self.triverts))

        # draw lines
        glUseProgram(self.lineProgram)

        glBindBuffer (GL_ARRAY_BUFFER, self.linevertbuf)
        glVertexPointer (4, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.linecolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)
    
        glDrawArrays (GL_LINES, 0, len(self.lineverts))
