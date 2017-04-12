import os

from OpenGL.GL import *

import numpy as np

def load_shader_src(shader_file):
    with open(shader_file) as f:
        return f.read()

# Provide a terse way to get a uniform location from its name
def U(name):
    p = glGetIntegerv(GL_CURRENT_PROGRAM)
    return glGetUniformLocation(p, name)

def A(name):
    p = glGetIntegerv(GL_CURRENT_PROGRAM)
    return glGetAttribLocation(p, name)

# Provide a terse way to create a f32 numpy 3-tuple
def V3(x, y, z):
    return np.array([x, y, z], 'f')

def translation(direction):
    M = np.identity(4)
    M[:3, 3] = direction[:3]
    return M

def scale(factor):
    m = np.identity(4)
    m[0, 0] = factor[0]
    m[1, 1] = factor[1]
    m[2, 2] = factor[2]

    return m
