import os

from ctypes import sizeof, c_float, c_void_p, c_uint

from opengl_utils import load_shader_src
from opengl_utils import U, A, V3, translation, scale

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

shaders_path = os.path.join(os.path.dirname(__file__), 'shaders')

def _init_circle_shaders():
    v_s = compileShader(load_shader_src(os.path.join(shaders_path, 'circle.vert')), GL_VERTEX_SHADER)
    f_s = compileShader(load_shader_src(os.path.join(shaders_path, 'circle.frag')), GL_FRAGMENT_SHADER)

    program = compileProgram(
        v_s,
        f_s
        )

    return program

def _init_buffers():
    #/* We only use one VAO, so we always keep it bound */
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #/* This is the buffer that holds the vertices */
    buffer = glGenBuffers(1)

    return(vao, buffer)

def _set_buffer_data(buffer, vertex_data, color):
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glBufferData(GL_ARRAY_BUFFER,
                     len(vertex_data) * 4 + len(color) * 4,
                     c_void_p(0),
                     GL_STATIC_DRAW)
    glBufferSubData(GL_ARRAY_BUFFER,
                        0,
                        len(vertex_data) * 4,
                        (GLfloat * len(vertex_data))(*vertex_data))
    glBufferSubData(GL_ARRAY_BUFFER,
                        len(vertex_data) * 4,
                        len(color) * 4,
                        (GLfloat * len(color))(*color))

class DrawCirclesData(object):
    def __init__(self):
        super().__init__()

        self.program = None
        self.vao = 0
        self.buffer = 0

        self._created = False

    def create(self):
        if self._created:
            return

        self.vao, self.buffer = _init_buffers()
        self.program = _init_circle_shaders()

        self._created = True

_draw_circles_data = DrawCirclesData()

#vertex_data is 4 point of the quad circle will draw in
def draw_circles(center, radius, color, viewport, t = translation([-0.0, -0.0, 0.0]), s = scale([1.0, 1.0, 1.0])):
    _draw_circles_data.create()

    x, y = center[0], center[1]

    x_delta = float(radius) * 2 / viewport[2]
    y_delta = float(radius) * 2 / viewport[3]

    vertex_data = [
        x - x_delta, y - y_delta,
        x - x_delta, y + y_delta,
        x + x_delta, y - y_delta,
        x + x_delta, y + y_delta
    ]

    color_data = color * int(len(vertex_data) / 2)

    glUseProgram(_draw_circles_data.program)

    glUniformMatrix4fv(U("translate"), 1, True, t)
    glUniformMatrix4fv(U("scale"), 1, True, s)

    glUniform2f(U("ViewportOffset"), (GLfloat)(viewport[0]), (GLfloat)(viewport[1]))
    glUniform2f(U("Viewport"), (GLfloat)(viewport[2]), (GLfloat)(viewport[3]))
    glUniform2f(U("Center"), (GLfloat)(x), (GLfloat)(y))
    glUniform1f(U("Radius"), (GLfloat)(radius))

    _set_buffer_data(_draw_circles_data.buffer, vertex_data, color_data)

    glEnableVertexAttribArray(A("Vertex"))
    glVertexAttribPointer(A("Vertex"), 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0));

    glEnableVertexAttribArray(A("Color"))
    glVertexAttribPointer(A("Color"), 4, GL_FLOAT, GL_FALSE, 0, c_void_p(len(vertex_data) * 4));

    glDrawArrays(GL_TRIANGLE_STRIP, 0, int(len(vertex_data) / 2))

    glDisableVertexAttribArray(A("Vertex"))
    glDisableVertexAttribArray(A("Color"))

    glUseProgram(0)
