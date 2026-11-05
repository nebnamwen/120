import pygame
import numpy
from math import *
from OpenGL.GL import *
from OpenGL.GL import shaders
from OpenGL.GL.EXT.geometry_shader4 import *

class _shader:
    LINES = (GL_LINES, GL_LINE_STRIP, 2)
    TRIANGLES = (GL_TRIANGLES, GL_TRIANGLE_STRIP, 3)

    vertex = None
    geometry = None
    fragment = '''
#version 120

void main()
{
    gl_FragColor = gl_Color;
}
'''

    def __init__(self, substitutions):
        if not self.vertex:
            raise NotImplementedError

        program = {}
        for code, kind in [ (self.vertex, GL_VERTEX_SHADER),
                            (self.geometry, GL_GEOMETRY_SHADER),
                            (self.fragment, GL_FRAGMENT_SHADER) ]:
            if code is not None:
                for s in substitutions:
                    code = code.replace(s, substitutions[s])

                program[kind] = shaders.compileShader(code, kind)

        self.lineProgram = self.shaderProgramForType(program, *self.LINES)
        self.triProgram = self.shaderProgramForType(program, *self.TRIANGLES)

    @staticmethod
    def shaderProgramForType(compiledShaders, input_t, output_t, verts):
        shaderProgram = glCreateProgram()

        for s in compiledShaders:
            glAttachShader(shaderProgram, compiledShaders[s])

        if GL_GEOMETRY_SHADER in compiledShaders:
            glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_INPUT_TYPE_EXT, input_t)
            glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_OUTPUT_TYPE_EXT, output_t)
            glProgramParameteriEXT(shaderProgram, GL_GEOMETRY_VERTICES_OUT_EXT, verts)

        glLinkProgram(shaderProgram)
        return shaderProgram

class mercator(_shader):
    vertex = '''
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

    geometry = '''
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

class canvas2D(_shader):
    vertex = '''
#version 120

void main()
{
    float x = (gl_Vertex.x / __VIEWPORT_WIDTH__) * 2.0 - 1.0;
    float y = 1.0 - (gl_Vertex.y / __VIEWPORT_HEIGHT__) * 2.0;
    gl_Position = vec4(x, y, 0.0, 1.0);
    gl_FrontColor = gl_Color;
}
'''

class display:
    def __init__(self, bg_color, name):
        bg_color_alpha = bg_color + (1.0,)
        bg_color_string = str(bg_color_alpha)

        self.viewport = (1200,600)

        pygame.init()
        pygame.display.set_mode (self.viewport, pygame.OPENGL|pygame.DOUBLEBUF, 24)
        pygame.display.set_caption(name)
        glViewport (0, 0, *self.viewport)

        glClearColor(*bg_color_alpha)

        mercatorProgram = mercator({'__BACKGROUND_COLOR__': bg_color_string})

        # background, object, and cursor layers
        self.layers = [ _layer(mercatorProgram, 4) for i in range(3) ]

        canvas2Dprogram = canvas2D({'__VIEWPORT_WIDTH__': str(self.viewport[0]),
                                    '__VIEWPORT_HEIGHT__': str(self.viewport[1])})
        self.overlayers = [ _layer(canvas2Dprogram, 2) for i in range(2) ]

        glEnableClientState (GL_VERTEX_ARRAY)
        glEnableClientState (GL_COLOR_ARRAY)

        self.view_matrix = numpy.identity(4)
        self.cursor_ray = numpy.zeros(4)

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

        mouse = pygame.mouse.get_pos()
        # these calcuations are the inverse of the projection in the Mercator vertex shader
        #        atan(position.x, position.z) / PI,
        #        tan(asin(position.y / length(position.xyz))) / PI_2,
        # if other projections are added, this should be encapsulated with the projection
        clx, cly = mouse[0]/self.viewport[0] * 2 - 1, 1 - mouse[1]/self.viewport[1] * 2
        cry = sin(atan(cly * pi / 2))
        crx = sin(clx * pi) * sqrt(1 - cry*cry)
        crz = cos(clx * pi) * sqrt(1 - cry*cry)
        self.cursor_ray = numpy.array([crx,cry,crz,0])

    def draw(self):
        glLoadMatrixf(numpy.concatenate(self.view_matrix.T, dtype=numpy.float32))

        glClear (GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_DEPTH_TEST)
        for l in self.layers:
            l.draw()
            
        glDisable(GL_DEPTH_TEST)
        for l in self.overlayers:
            l.draw()

        pygame.display.flip ()
        pygame.time.wait(10)

    def quit(self):
        pygame.quit()

    def cursor_ray_check(self, points):
        for k, v, r in points:
            v = self.view_matrix.dot(v)

            w = v[3]
            v[3] = 0
            z = v.dot(self.cursor_ray)
            x = numpy.linalg.norm(v - self.cursor_ray * z)

            if z > r and x < r and w >= -0.5:
                yield (-w, k)

class _layer():
    def __init__(self, shader, dimension):
        self.shader = shader
        self.dimension = dimension

        self.triverts = []
        self.tricolors = []
        self.lineverts = []
        self.linecolors = []

        self.tridirty = False
        self.linedirty = False

        self.trivertbuf, self.tricolbuf, self.linevertbuf, self.linecolbuf = glGenBuffers(4)

    def clear(self):
        self.triverts = []
        self.tricolors = []
        self.lineverts = []
        self.linecolors = []

        self.tridirty = True
        self.linedirty = True

    def triangle(self, key, a,b,c, color):
        self.tridirty = True

        for v in (a,b,c):
            self.triverts.append((key,numpy.array(v)))
            self.tricolors.append((key,numpy.array(color)))

    def line(self, key, a,b, color):
        self.linedirty = True

        for v in (a,b):
            self.lineverts.append((key,numpy.array(v)))
            self.linecolors.append((key,numpy.array(color)))

    def remove(self, *keys):
        keys = set(keys)

        self.triverts = [i for i in self.triverts if i[0] not in keys]
        self.tricolors = [i for i in self.tricolors if i[0] not in keys]
        self.lineverts = [i for i in self.lineverts if i[0] not in keys]
        self.linecolors = [i for i in self.linecolors if i[0] not in keys]

        self.tridirty = True
        self.linedirty = True

    @staticmethod
    def _bufferdata(b, l):
        glBindBuffer (GL_ARRAY_BUFFER, b)
        data = numpy.array([])
        if l:
            data = numpy.concatenate([i[1] for i in l], dtype=numpy.float32)
        glBufferData (GL_ARRAY_BUFFER, data.nbytes, data, GL_STATIC_DRAW)

    def draw(self):
        if self.tridirty:
            _layer._bufferdata(self.trivertbuf, self.triverts)
            _layer._bufferdata(self.tricolbuf, self.tricolors)
            self.tridirty = False

        if self.linedirty:
            _layer._bufferdata(self.linevertbuf, self.lineverts)
            _layer._bufferdata(self.linecolbuf, self.linecolors)
            self.linedirty = False

        # draw triangles
        glUseProgram(self.shader.triProgram)

        glBindBuffer(GL_ARRAY_BUFFER, self.trivertbuf)
        glVertexPointer(self.dimension, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.tricolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)

        glDrawArrays (GL_TRIANGLES, 0, len(self.triverts))

        # draw lines
        glUseProgram(self.shader.lineProgram)

        glBindBuffer (GL_ARRAY_BUFFER, self.linevertbuf)
        glVertexPointer (self.dimension, GL_FLOAT, 0, None)

        glBindBuffer (GL_ARRAY_BUFFER, self.linecolbuf)
        glColorPointer (3, GL_FLOAT, 0, None)

        glDrawArrays (GL_LINES, 0, len(self.lineverts))
