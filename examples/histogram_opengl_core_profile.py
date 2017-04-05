"""
 Shows an histogram window

"""
import random
from pylibui.core import App
from pylibui.controls import *
from pylibui import libui
from OpenGL.GL import *

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
  0.,   0.5,   0., 1.,
  0.5, -0.366, 0., 1.,
 -0.5, -0.366, 0., 1.,
]

from ctypes import sizeof, c_float, c_void_p, c_uint

def init_buffers():
    #/* We only use one VAO, so we always keep it bound */
    vao = glGenVertexArrays(1);
    glBindVertexArray(vao);

    #/* This is the buffer that holds the vertices */
    buffer = glGenBuffers(1);
    glBindBuffer(GL_ARRAY_BUFFER, buffer);
    glBufferData(GL_ARRAY_BUFFER, (c_float*len(vertex_data))(*vertex_data), GL_STATIC_DRAW);
    glBindBuffer(GL_ARRAY_BUFFER, 0);

    print(vao, buffer)
    return(vao, buffer)

def create_shader(type, src):
    shader = glCreateShader(type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    status = glGetShaderiv(shader, GL_COMPILE_STATUS)
    if(status == GL_FALSE):
        print("Compile failure in %s shader:\n%s" %(
            "vertex" if type == GL_VERTEX_SHADER else "fragment",
            glGetShaderInfoLog(shader)))
        glDeleteShader(shader);

        return None

    print('status:', status, GL_FALSE)
    return shader

def read_src(path):
    with open(path, 'rb') as f:
        return f.read()

fragment_src = '''
#version 330

out vec4 outputColor;

void main() {
  float lerpVal = gl_FragCoord.y / 500.0f;

  outputColor = mix(vec4(1.0f, 0.85f, 0.35f, 1.0f), vec4(0.2f, 0.2f, 0.2f, 1.0f), lerpVal);
}
'''

vertex_src = '''
#version 330

layout(location = 0) in vec4 position;
uniform mat4 mvp;

void main() {
  gl_Position = mvp * position;
}
'''

def init_shaders(vertex_path, fragment_path):
    vertex = create_shader(GL_VERTEX_SHADER, vertex_src);

    if not vertex:
        return(None, None)
  
    fragment = create_shader(GL_FRAGMENT_SHADER, fragment_src);

    if not fragment:
        glDeleteShader(vertex);
        return(None, None)

    print(vertex, fragment)
    
    program = glCreateProgram();
    glAttachShader(program, vertex);
    glAttachShader(program, fragment);

    glLinkProgram(program);

    status = glGetProgramiv(program, GL_LINK_STATUS);
    if status == GL_FALSE:
        print("Linking failure:\n%s" % glGetProgramInfoLog(program));
        glDeleteProgram(program);
        glDeleteShader(vertex);
        glDeleteShader(fragment);

        return(None, None)

    #/* Get the location of the "mvp" uniform */
    mvp = glGetUniformLocation(program, "mvp");

    glDetachShader(program, vertex);
    glDetachShader(program, fragment);
    glDeleteShader(vertex);
    glDeleteShader(fragment);

    print(status, program, mvp)
    return(program, mvp)

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
    c3s2s1 = c3 * s2 * s1;
    s3s1 = s3 * s1;
    c3s2c1 = c3 * s2 * c1;
    s3c2 = s3 * c2;
    c3c1 = c3 * c1;
    s3s2s1 = s3 * s2 * s1;
    c3s1 = c3 * s1;
    s3s2c1 = s3 * s2 * c1;
    c2s1 = c2 * s1;
    c2c1 = c2 * c1;

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

    return res

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

class MyArea(OpenGLArea):
    def __init__(self):
        super().__init__()

    def onDraw(self, params):
        glClearColor(0.5, .5, 0.5, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        self.drawObject2()
        glFlush()

    def drawObject2(self):
        vao, buffer = init_buffers()
        program, mvp_location = init_shaders('glarea-gl.vs.glsl', 'glarea-gl.fs.glsl')

        mvp = compute_mvp(datapoints[0].getValue(),
                              datapoints[1].getValue(),
                              datapoints[2].getValue())

        glUseProgram (program);

        #/* Update the "mvp" matrix we use in the shader */
        glUniformMatrix4fv (mvp_location, 1, GL_FALSE, mvp);

        #/* Use the vertices in our buffer */
        glBindBuffer (GL_ARRAY_BUFFER, vao);
        glEnableVertexAttribArray (0);
        glVertexAttribPointer (0, 4, GL_FLOAT, GL_FALSE, 0, 0);

        #/* Draw the three vertices as a triangle */
        glDrawArrays (GL_TRIANGLES, 0, 3);

        #/* We finished using the buffers and program */
        glDisableVertexAttribArray (0);
        glBindBuffer (GL_ARRAY_BUFFER, 0)
        glUseProgram (0);
        
        glDeleteBuffers (1, vao)
        glDeleteProgram (program)
        
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
