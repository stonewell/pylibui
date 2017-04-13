import os

from ctypes import sizeof, c_float, c_void_p, c_uint

from opengl_utils import load_shader_src
from opengl_utils import U, A, V3, translation, scale

from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

shaders_path = os.path.join(os.path.dirname(__file__), 'shaders')

def _init_line_shaders():
    v_s = compileShader(load_shader_src(os.path.join(shaders_path, 'polyline.vert')), GL_VERTEX_SHADER)
    f_s = compileShader(load_shader_src(os.path.join(shaders_path, 'polyline.frag')), GL_FRAGMENT_SHADER)
    g_s = compileShader(load_shader_src(os.path.join(shaders_path, 'polyline.geom')), GL_GEOMETRY_SHADER)

    program = compileProgram(
        v_s,
        g_s,
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

class DrawLinesData(object):
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
        self.program = _init_line_shaders()

        self._created = True

_draw_lines_data = DrawLinesData()

def draw_lines(vertex_data_origin, color_data_origin, thickness, viewport):
    _draw_lines_data.create()

    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST)

    glUseProgram(_draw_lines_data.program)

    t = translation([-1.0, -1.0, 0.0])
    s = scale([2.0, 2.0, 1.0])

    #add the adjacency point
    vertex_data = vertex_data_origin[:]
    color_data = color_data_origin[:]
    
    vertex_data.insert(0, 0.0)
    vertex_data.insert(0, 0.0)
    vertex_data.append(1.0)
    vertex_data.append(0.0)
    color_data.insert(0, 1.0)
    color_data.insert(0, 1.0)
    color_data.insert(0, 1.0)
    color_data.insert(0, 0.0)
    color_data.append(1.0)
    color_data.append(1.0)
    color_data.append(1.0)
    color_data.append(0.0)
    
    glUniformMatrix4fv(U("translate"), 1, True, t)
    glUniformMatrix4fv(U("scale"), 1, True, s)

    #glUniformMatrix4fv(U("ModelViewProjectionMatrix"), 1, True, s)
    glUniform2f(U("Viewport"), (GLfloat)(viewport[0]), (GLfloat)(viewport[1]))
    glUniform1f(U("Thickness"), (GLfloat)(thickness))
    glUniform1f(U("MiterLimit"), (GLfloat)(.1))

    _set_buffer_data(_draw_lines_data.buffer, vertex_data, color_data)
    
    glEnableVertexAttribArray(A("Vertex"))
    glVertexAttribPointer(A("Vertex"), 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0));

    glEnableVertexAttribArray(A("Color"))
    glVertexAttribPointer(A("Color"), 4, GL_FLOAT, GL_FALSE, 0, c_void_p(len(vertex_data) * 4));
    
    glDrawArrays(GL_LINE_STRIP_ADJACENCY, 0, int(len(vertex_data) / 2))

    glDisableVertexAttribArray(A("Vertex"))
    glDisableVertexAttribArray(A("Color"))
    
    glUseProgram(0)
    
    glDisable(GL_LINE_SMOOTH)

