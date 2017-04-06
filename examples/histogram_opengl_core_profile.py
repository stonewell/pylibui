"""
 Shows an histogram window

"""
import random
from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram

histogram = None
datapoints = []

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
    vao = GL.glGenVertexArrays(1)
    GL.glBindVertexArray(vao)

    #/* This is the buffer that holds the vertices */
    buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER,
                     len(vertex_data) * 4,
                     (GL.GLfloat*len(vertex_data))(*vertex_data),
                        GL.GL_STATIC_DRAW)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

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
    v_s = compileShader(vertex_src, GL.GL_VERTEX_SHADER)
    f_s = compileShader(fragment_src, GL.GL_FRAGMENT_SHADER)
    program = compileProgram(
        v_s,
        f_s
        )

    return (program, 0)


class MyArea(OpenGLArea):
    def __init__(self):
        super().__init__()
        self._program = None
        self._buffer = None

    def onDraw(self, params):
        GL.glClearColor(0.5, .5, 0.5, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        self.drawObject2()
        GL.glFlush()
        
    def drawObject2(self):
        if self._buffer is None:
            vao, self._buffer = init_buffers()

        if self._program is None:
            self._program, mvp_location = init_shaders()

        GL.glUseProgram(self._program)

        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self._buffer)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0));

        #/* Draw the three vertices as a triangle */
        GL.glDrawArrays(GL.GL_TRIANGLES, 0, 12)

        #/* We finished using the buffers and program */
        GL.glDisableVertexAttribArray(0)
        GL.glUseProgram(0)
        
    def onMouseEvent(self, e):
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
