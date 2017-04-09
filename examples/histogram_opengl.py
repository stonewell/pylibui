"""
 Shows an histogram window

"""
import random
from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram

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

def graphSize(clientWidth, clientHeight):
    return (clientWidth - xoffLeft - xoffRight,
                clientHeight - yoffTop - yoffBottom)

def inPoint(x, y, xtest, ytest):
    # TODO switch to using a matrix
    x -= xoffLeft
    y -= yoffTop

    return ((x >= xtest - pointRadius) and
                (x <= xtest + pointRadius) and
                (y >= ytest - pointRadius) and
                (y <= ytest + pointRadius))

def pointLocations(width, height):
    xincr, yincr = float(width) / 9, float(height) / 100

    i = 0
    xs = []
    ys = []
    for spinbox in datapoints:
        n = 100 - spinbox.getValue()

        xs.append(xincr * i)
        ys.append(yincr * n)

        i += 1

    return xs, ys

def constructGraph(width, height, extend):
    xs, ys = pointLocations(width, height)
    path = libui.uiDrawNewPath(libui.uiDrawFillModeWinding)

    libui.uiDrawPathNewFigure(path, xs[0], ys[0])

    for i in range(1, 10):
        libui.uiDrawPathLineTo(path, xs[i], ys[i])

    if extend:
        libui.uiDrawPathLineTo(path, width, height);
        libui.uiDrawPathLineTo(path, 0, height);
        libui.uiDrawPathCloseFigure(path);

    libui.uiDrawPathEnd(path)

    return path

vertex_data = [
    0.0, 0.0,
    0.5, 0.0,
    0.5, 0.5,

    0.0, 0.0,
    0.0, 0.5,
    -0.5, 0.5,

    0.0, 0.0,
    -0.5, 0.0,
    -0.5, -0.5,

    0.0, 0.0,
    0.0, -0.5,
    0.5, -0.5,
]

from ctypes import sizeof, c_float, c_void_p, c_uint

def init_buffers():
    #/* We only use one VAO, so we always keep it bound */
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    #/* This is the buffer that holds the vertices */
    buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)
    glBufferData(GL_ARRAY_BUFFER,
                     len(vertex_data) * 4,
                     (GLfloat*len(vertex_data))(*vertex_data),
                        GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    return(vao, buffer)

fragment_src = '''
#version 150

out vec4 outputColor;

void main() {
  outputColor = vec4(1.0f, 0.f, 0.f, 1.0f);
}
'''

vertex_src = '''
#version 150

in vec4 position;

void main() {
  gl_Position = position;
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

class MyArea(OpenGLArea):
    def __init__(self):
        super().__init__()
        self._program = None
        self._buffer = None

    def onDraw(self, params):
        glClearColor(0, 1, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)

        if (isOpenGLCoreProfile()):
            self.drawObject2_CoreProfile()
        else:
            self.drawObject2_Legacy()
        glFlush()

    def drawObject2_Legacy(self):
        glMatrixMode(GL_PROJECTION)

        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        glColor3f(1.0, 0.85, 0.35)

        glBegin(GL_TRIANGLES)
        glVertex3f( 0.0,  1.0, 0.0)
        glVertex3f(-1.0, -1.0, 0.0)
        glVertex3f( 1.0, -1.0, 0.0)
        glEnd()

    def drawObject2_CoreProfile(self):
        if self._buffer is None:
            vao, self._buffer = init_buffers()

        if self._program is None:
            self._program, mvp_location = init_shaders()

        glUseProgram(self._program)

        glBindBuffer(GL_ARRAY_BUFFER, self._buffer)
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, c_void_p(0));

        #/* Draw the three vertices as a triangle */
        glDrawArrays(GL_TRIANGLES, 0, 12)

        #/* We finished using the buffers and program */
        glDisableVertexAttribArray(0)
        glUseProgram(0)

    def onMouseEvent(self, e):
        graphWidth, graphHeight = graphSize(e.AreaWidth, e.AreaHeight)
        xs, ys = pointLocations(graphWidth, graphHeight)

        found = -1
        for i in range(10):
            if inPoint(e.X, e.Y, xs[i], ys[i]):
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
