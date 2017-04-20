"""
 Shows an histogram window

"""
import sys
import random

from ctypes import sizeof, c_float, c_void_p, c_uint

from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import numpy as np

from opengl_utils import U, A, V3, translation, scale
from opengl_line import draw_lines
from opengl_circle import draw_circles

histogram = None

class MyWindow(Window):

    def onClose(self, data):
        super().onClose(data)
        app.stop()

class MySpinBox(Spinbox):

    def onChanged(self, data):
        super().onChanged(data)
        histogram.redrawAll()

class MyColorButton(ColorButton):

    def onColorChanged(self, data):
        super().onColorChanged(data)
        histogram.redrawAll()

xoffLeft = 20
yoffTop = 20
xoffRight = 20
yoffBottom = 20
pointRadius = 5

colorButton = None
datapoints = []
currentPoint = -1

AreaWidth = 0
AreaHeight = 0

x_scale_factor = 2.0
y_scale_factor = 2.0
x_translate_factor = -1.0
y_translate_factor = -1.0

def graphSize(clientWidth, clientHeight):
    return (clientWidth - xoffLeft - xoffRight,
                clientHeight - yoffTop - yoffBottom)

def inPoint(x, y, xtest, ytest):
    xtest = (xtest * x_scale_factor * (AreaWidth - xoffLeft - xoffRight) / 2
                 + x_translate_factor * (AreaWidth - xoffLeft - xoffRight) / 2
                 + (AreaWidth - xoffLeft - xoffRight) / 2)
    ytest = (ytest * y_scale_factor * (AreaHeight - yoffTop - yoffBottom) / 2
                 + y_translate_factor * (AreaHeight - yoffTop - yoffBottom) / 2
                 + (AreaHeight - yoffTop - yoffBottom) / 2)

    xtest += xoffLeft
    ytest = AreaHeight - ytest - yoffBottom

    return ((x >= xtest - pointRadius) and
                (x <= xtest + pointRadius) and
                (y >= ytest - pointRadius) and
                (y <= ytest + pointRadius))

def pointLocations(linesOnly = False):
    i = 0
    vertex_data = []

    if not linesOnly:
        vertex_data.extend([0.0, 0.0])

    for spinbox in datapoints:
        n = spinbox.getValue()

        vertex_data.append(float(i) / 9 )
        vertex_data.append(float(n) / 100)

        if not linesOnly:
            if i < len(datapoints) - 1:
                vertex_data.append(float(i + 1) / 9 )
                vertex_data.append(0)

        i += 1

    return vertex_data

def init_buffers():
    #/* We only use one VAO, so we always keep it bound */
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #/* This is the buffer that holds the vertices */
    buffer = glGenBuffers(1)

    return(vao, buffer)

def set_buffer_data(buffer, vertex_data, color):
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

fragment_src = '''
#version 150

in vec4 colorFromVertexShader;
out vec4 outputColor;

void main() {
  outputColor = colorFromVertexShader;
}
'''

vertex_src = '''
#version 150

uniform mat4 translate;
uniform mat4 scale;
in vec4 position;
in vec4 inputColor;
out vec4 colorFromVertexShader;

void main() {
  gl_Position = translate * scale * position;
  colorFromVertexShader = inputColor;
}
'''

def init_shaders():
    v_s = compileShader(vertex_src, GL_VERTEX_SHADER)
    f_s = compileShader(fragment_src, GL_FRAGMENT_SHADER)
    program = compileProgram(
        v_s,
        f_s
        )

    return (program, 0)

def isOpenGLCoreProfile():
    version = str(glGetString(GL_VERSION), 'utf-8').split(' ')[0]

    major = int(version.split('.')[0])

    return major >= 3

class MyArea(ScrollingOpenGLArea):
    def __init__(self):
        super().__init__(1920, 1280)
        self._program = None
        self._buffer = None

    def onDraw(self, params):
        width, height = int(params.AreaWidth), int(params.AreaHeight)

        msaa = not sys.platform.startswith('linux')

        if msaa:
            tex = glGenTextures(1)
            glBindTexture( GL_TEXTURE_2D_MULTISAMPLE, tex )
            glTexImage2DMultisample( GL_TEXTURE_2D_MULTISAMPLE, 8, GL_RGBA8, width, height, False )

            fbo = glGenFramebuffers( 1 )
            glBindFramebuffer( GL_FRAMEBUFFER, fbo );
            glFramebufferTexture2D( GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D_MULTISAMPLE, tex, 0 );

        glClearColor(1.0, 1.0, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT,  GL_NICEST)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        if (isOpenGLCoreProfile()):
            self.drawObject2_CoreProfile(params)
        else:
            self.drawObject2_Legacy()

        if msaa:
            glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
            glBindFramebuffer(GL_READ_FRAMEBUFFER, fbo)
            glDrawBuffer(GL_BACK)
            glBlitFramebuffer(0, 0, width, height,
                                  0, 0, width,height,
                                  GL_COLOR_BUFFER_BIT, GL_NEAREST)
            glDeleteTextures(tex)
        glFlush()

    def drawObject2_Legacy(self):
        glMatrixMode(GL_PROJECTION)

        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)

        glColor3f(1.0, 0.85, 0.35)

        glBegin(GL_TRIANGLES)
        glVertex3f( 0.0,  1.0, 0.0)
        glVertex3f(-1.0, -1.0, 0.0)
        glVertex3f( 1.0, -1.0, 0.0)
        glEnd()

    def drawObject2_CoreProfile(self, params):
        if self._buffer is None:
            vao, self._buffer = init_buffers()

        if self._program is None:
            self._program, mvp_location = init_shaders()

        #save the Area size
        global AreaWidth
        global AreaHeight
        AreaWidth, AreaHeight = params.AreaWidth, params.AreaHeight
        
        viewport_x = -int(params.ClipX) + xoffLeft
        viewport_y = -int(params.AreaHeight) + int(params.ClipY) + int(params.ClipHeight) + yoffBottom

        glUseProgram(self._program)

        t = translation([x_translate_factor, y_translate_factor, 0.0])
        s = scale([x_scale_factor, y_scale_factor, 1.0])

        glUniformMatrix4fv(U("translate"), 1, True, t)
        glUniformMatrix4fv(U("scale"), 1, True, s)

        graphR, graphG, graphB, graphA = colorButton.getColor();

        vertex_data = pointLocations()

        color = [graphR, graphG, graphB, graphA * 0.5] * int(len(vertex_data) / 2)

        set_buffer_data(self._buffer, vertex_data, color)

        glEnableVertexAttribArray(A('position'))
        glVertexAttribPointer(A('position'), 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0));

        glEnableVertexAttribArray(A('inputColor'))
        glVertexAttribPointer(A('inputColor'), 4, GL_FLOAT, GL_FALSE, 0, c_void_p(len(vertex_data) * 4));

        glViewport(viewport_x,
                       viewport_y,
                       int(params.AreaWidth) - xoffRight - xoffLeft,
                       int(params.AreaHeight) - yoffBottom - yoffTop)
        #/* Draw the three vertices as a triangle */
        glDrawArrays(GL_TRIANGLE_STRIP, 0, int(len(vertex_data) / 2))

        #Draw Axis
        axis = [
            -1.0, -1.0,
            -1.0, 1.0,
            1.0, -1.0,
            1.0, 1.0
        ]

        axis_color = [0.0, 0.0, 0.0, 1.0] * int(len(axis) / 2)
        set_buffer_data(self._buffer, axis, axis_color)
        glEnableVertexAttribArray(A('position'))

        glVertexAttribPointer(A('position'), 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0));

        glEnableVertexAttribArray(A('inputColor'))
        glVertexAttribPointer(A('inputColor'), 4, GL_FLOAT, GL_FALSE, 0, c_void_p(len(axis) * 4));

        #X
        glViewport(viewport_x - 3,
                        viewport_y - 3,
                       int(params.AreaWidth - xoffLeft + 3 - xoffRight),
                       3)
        glDrawArrays(GL_TRIANGLE_STRIP, 0, int(len(axis) / 2))

        #Y
        glViewport(viewport_x - 3,
                        viewport_y - 3,
                       3,
                       int(params.AreaHeight - yoffBottom + 3 - yoffTop))
        glDrawArrays(GL_TRIANGLE_STRIP, 0, int(len(axis) / 2))

        glDisableVertexAttribArray(0)

        #draw thick lines
        vertex_data = pointLocations(True)

        color = [graphR, graphG, graphB, graphA] * int(len(vertex_data) / 2)

        viewport = [int(params.AreaWidth) - xoffRight - xoffLeft, int(params.AreaHeight) - yoffBottom - yoffTop]
        glViewport(viewport_x,
                        viewport_y,
                       viewport[0],
                       viewport[1])
        draw_lines(vertex_data, color, 3, viewport, t, s)

        #draw circles
        vertex_data = pointLocations(True)
        color = [graphR, graphG, graphB, graphA] * int(len(vertex_data) / 2)

        viewport = [int(params.AreaWidth) - xoffRight - xoffLeft, int(params.AreaHeight) - yoffBottom - yoffTop]

        glViewport(viewport_x, viewport_y, viewport[0], viewport[1])

        for i in range(0, len(vertex_data), 2):
            x, y = vertex_data[i], vertex_data[i + 1]

            if i == currentPoint:
                circle_color = [1.0, 0.0, 0.0, 1.0]
            else:
                circle_color = [graphR, graphG, graphB, graphA]

            draw_circles([x, y], pointRadius, circle_color, [viewport_x, viewport_y, viewport[0], viewport[1]], t, s);

        #/* We finished using the buffers and program */
        glUseProgram(0)

    def onMouseEvent(self, e):
        vertex_data = pointLocations(True)

        found = -1

        for i in range(0, len(vertex_data), 2):
            if inPoint(e.X, e.Y, vertex_data[i], vertex_data[i + 1]):
                found = i
                break

        global currentPoint
        currentPoint = found

        #TODO only redraw the relevant area
        self.redrawAll()

app = App()

window = MyWindow('pylibui Histogram Example', 640, 480)
window.setMargined(True)

hbox = HorizontalBox()
hbox.setPadded(1)
window.setChild(hbox)

vbox = VerticalBox()
vbox.setPadded(1)
hbox.append(vbox)

for i in range(10):
    spinbox = MySpinBox(0, 100)
    spinbox.setValue(random.randint(0, 100))
    datapoints.append(spinbox)
    vbox.append(spinbox)

colorButton = MyColorButton()
colorButton.setColor((float(0x1E) / 255, float(0x90) / 255, float(0xFF) / 255, 1))
vbox.append(colorButton)

histogram = MyArea()
hbox.append(histogram, True)

window.show()

app.start()
app.close()
