"""
 Shows an histogram window

"""
import random
from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL.GL import *

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

class MyArea(OpenGLArea):
    def __init__(self):
        super().__init__()

    def onDraw(self, params):
        glClearColor(0, 1, 0, 0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.drawObject2()
        glFlush()

    def drawObject2(self):
        glMatrixMode(GL_PROJECTION)
        
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glDisable(GL_CULL_FACE)
        glDisable(GL_LIGHTING)
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        glColor3f(1.0, 0.85, 0.35)
        #glTranslatef(-1.5,0.0,-6.0)
        
        glBegin(GL_TRIANGLES)
        glVertex3f( 0.0,  1.0, 0.0)
        glVertex3f(-1.0, -1.0, 0.0)
        glVertex3f( 1.0, -1.0, 0.0)
        glEnd()
        
        #glTranslatef(3.0,0.0,0.0);
        #glBegin(GL_QUADS)
        #glVertex3f(-1.0,-1.0, 0.0)
        #glVertex3f( 1.0,-1.0, 0.0)
        #glVertex3f( 1.0, 1.0, 0.0)
        #glVertex3f(-1.0, 1.0, 0.0)
        #glEnd()

        glFlush()

    def drawObject(self):
        glColor3f(1.0, 0.85, 0.35)
        glBegin(GL_TRIANGLES)

        glVertex3f(  0.0,  0.6, 0.0)
        glVertex3f( -0.2, -0.3, 0.0)
        glVertex3f(  0.2, -0.3 ,0.0)

        glEnd()
        
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
