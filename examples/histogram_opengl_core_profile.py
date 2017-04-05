"""
 Shows an histogram window

"""
import random
from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL import GL
from OpenGL.GL.shaders import compileShader, compileProgram
from OpenGL.GL.ARB.vertex_array_object import glBindVertexArray
from glwrap import glGenVertexArray

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
    #vao = GL.glGenVertexArrays(1)
    #glBindVertexArray(vao)

    #/* This is the buffer that holds the vertices */
    buffer = GL.glGenBuffers(1)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
    GL.glBufferData(GL.GL_ARRAY_BUFFER,
                     len(vertex_data) * 4,
                     (GL.GLfloat*len(vertex_data))(*vertex_data),
                        GL.GL_STATIC_DRAW)
    GL.glBindBuffer(GL.GL_ARRAY_BUFFER, 0)

    return(0, buffer)

def create_shader(type, src):
    shader = glCreateShader(type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if(status == GL_FALSE):
        print("Compile failure in %s shader:\n%s" %(
            "vertex" if type == GL_VERTEX_SHADER else "fragment",
            glGetShaderInfoLog(shader)))
        glDeleteShader(shader)

        return None

    print('status:', status, GL_FALSE)
    return shader

def read_src(path):
    with open(path, 'rb') as f:
        return f.read()

fragment_src = '''
#version 130

out vec4 outputColor;

void main() {
  outputColor = vec4(1.0f, 0.f, 0.f, 1.0f);
}
'''

vertex_src = '''
#version 130

in vec4 position;

void main() {
  gl_Position = position;
}
'''

def init_shaders(vertex_path, fragment_path):
    v_s = compileShader(vertex_src, GL.GL_VERTEX_SHADER)
    f_s = compileShader(fragment_src, GL.GL_FRAGMENT_SHADER)
    program = compileProgram(
        v_s,
        f_s
        )

    GL.glDeleteShader(v_s)
    GL.glDeleteShader(f_s)
    return(program, 0)

G_PI = float(3.1415926535897932)

def compute_mvp(phi,
             theta,
             psi):
    import math
    x = float(phi *(G_PI / 180.))
    y = float(theta *(G_PI / 180.))
    z = float(psi *(G_PI / 180.))
    c1 = math.cos(x)
    s1 = math.sin(x)
    c2 = math.cos(y)
    s2 = math.sin(y)
    c3 = math.cos(z)
    s3 = math.sin(z)
    c3c2 = c3 * c2
    s3c1 = s3 * c1
    c3s2s1 = c3 * s2 * s1
    s3s1 = s3 * s1
    c3s2c1 = c3 * s2 * c1
    s3c2 = s3 * c2
    c3c1 = c3 * c1
    s3s2s1 = s3 * s2 * s1
    c3s1 = c3 * s1
    s3s2c1 = s3 * s2 * c1
    c2s1 = c2 * s1
    c2c1 = c2 * c1

    res = [0.0] * 16

            #/* initialize to the identity
    res[0] = 1.
    res[4] = 0.
    res[8] = 0.
    res[12] = 0.

    res[1] = 0.
    res[5] = 1.
    res[9] = 0.
    res[13] = 0.

    res[2] = 0.
    res[6] = 0.
    res[10] = 1.
    res[14] = 0.

    res[3] = 0.
    res[7] = 0.
    res[11] = 0.
    res[15] = 1.

        ## /* apply all three rotations using the three matrices:
        ##  *
        ##  * ⎡  c3 s3 0 ⎤ ⎡ c2  0 -s2 ⎤ ⎡ 1   0  0 ⎤
        ##  * ⎢ -s3 c3 0 ⎥ ⎢  0  1   0 ⎥ ⎢ 0  c1 s1 ⎥
        ##  * ⎣   0  0 1 ⎦ ⎣ s2  0  c2 ⎦ ⎣ 0 -s1 c1 ⎦
        ##  */
    res[0] = c3c2
    res[4] = s3c1 + c3s2s1
    res[8] = s3s1 - c3s2c1
    res[12] = 0.

    res[1] = -s3c2
    res[5] = c3c1 - s3s2s1
    res[9] = c3s1 + s3s2c1
    res[13] = 0.

    res[2] = s2
    res[6] = -c2s1
    res[10] = c2c1
    res[14] = 0.

    res[3] = 0.
    res[7] = 0.
    res[11] = 0.
    res[15] = 1.

    print(res)
    return res

from hello import display, init

class MyArea(OpenGLArea):
    def __init__(self):
        super().__init__()

    def onDraw(self, params):
        print('params', params.ClipWidth,params.ClipHeight)
        GL.glClearColor(0.5, .5, 0.5, 1.0)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT)
        #self.drawObject2()
        init()
        #display()
        GL.glFlush()
        #GL.glBindVertexArray( 0 )
        
    def drawObject2(self):
        program, mvp_location = init_shaders('glarea-gl.vs.glsl', 'glarea-gl.fs.glsl')

        vao, buffer = init_buffers()
        glBindVertexArray( glGenVertexArray() )

        mvp = compute_mvp(datapoints[0].getValue(),
                              datapoints[1].getValue(),
                              datapoints[2].getValue())

        GL.glUseProgram(program)

        #/* Update the "mvp" matrix we use in the shader */
        #glUniformMatrix4fv(mvp_location, 1, GL_FALSE, mvp)
        #position_attribute = glGetAttribLocation(program, "position")

        #/* Use the vertices in our buffer */
        #glBindVertexArray(vao)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
        GL.glEnableVertexAttribArray(0)
        GL.glVertexAttribPointer(0, 2, GL.GL_FLOAT, GL.GL_FALSE, 0, c_void_p(0));
        #glVertexAttribPointer(0, 4, GL_FLOAT, GL_FALSE, 0, 0)

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
