import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
from OpenGL.raw.GL.VERSION.GL_4_3 import GLDEBUGPROC

# ---------- Initialize GLFW ----------
if not glfw.init():
    raise Exception("GLFW init failed")

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
# glfw.window_hint(glfw.OPENGL_DEBUG_CONTEXT, glfw.TRUE)

window = glfw.create_window(400, 400, "OPENGLDEV", None, None)

if not window:
    glfw.terminate()
    raise Exception("Window creation failed")

glfw.make_context_current(window)

def resize(window, width, height):
    glViewport(0, 0, width, height)

glViewport(0, 0, 400, 400)
glfw.set_framebuffer_size_callback(window, resize)

# def debug_callback(source, type, id, severity, length, message, userParam):
#     print("OPENGL DEBUG:", message)
#
# glEnable(GL_DEBUG_OUTPUT)
# glEnable(GL_DEBUG_OUTPUT_SYNCHRONOUS)
#
# DEBUG_CLBK = GLDEBUGPROC(debug_callback)
# glDebugMessageCallback(DEBUG_CLBK, None)

# ---------- Shaders ----------
VERTEX_SHADER = """
#version 430 core
layout (location = 0) in vec3 aPos;
void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER = """
#version 430 core
out vec4 FragColor;
void main()
{
    FragColor = vec4(1.0, 0.5, 0.2, 1.0);
}
"""

class Program:
    def __init__(self, file_path: str):
        with open(file_path) as f:
            self.parse(f.readlines())
            self.compile_shaders()
            self.link_program()

    def parse(self, lines: list[str]):
        self.shader_src = {}
        shader_type = ""
        for line in lines:
            if line.startswith("#shader"):
                shader_type = line[len("#shader ") - 1:].strip()
                self.shader_src[shader_type] = ""
                continue
            self.shader_src[shader_type] += line

    def compile_shaders(self):
        # vertex
        if not "vertex" in self.shader_src.keys():
            print("ERROR: vertex shader missing")
            return
        self.vs = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(self.vs, self.shader_src["vertex"])
        glCompileShader(self.vs)
        if glGetShaderiv(self.vs, GL_COMPILE_STATUS) == GL_FALSE:
            print("SHADER ERROR: " + str(glGetShaderInfoLog(self.vs)))

        # fragment
        if not "fragment" in self.shader_src.keys():
            print("ERROR: fragment shader missing")
            return
        self.fs = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(self.fs, self.shader_src["fragment"])
        glCompileShader(self.fs)
        if glGetShaderiv(self.fs, GL_COMPILE_STATUS) == GL_FALSE:
            print("SHADER ERROR: " + str(glGetShaderInfoLog(self.fs)))

    def link_program(self):
        self.program = glCreateProgram()
        glAttachShader(self.program, self.vs)
        glAttachShader(self.program, self.fs)
        glLinkProgram(self.program)

        glDeleteShader(self.vs)
        glDeleteShader(self.fs)

    def use(self):
        glUseProgram(self.program)


prog1 = Program("shaders.glsl")

def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)

    if glGetShaderiv(shader, GL_COMPILE_STATUS) == GL_FALSE:
        print("SHADER ERROR: " + str(glGetShaderInfoLog(shader)))

    return shader


# ---------- Render loop ----------
while not glfw.window_should_close(window):
    # Input
    if (glfw.get_key(window, glfw.KEY_ESCAPE)) == glfw.PRESS:
        glfw.set_window_should_close(window, True)

    glClearColor(0.1, 0.1, 0.1, 1)
    glClear(GL_COLOR_BUFFER_BIT)

    glfw.poll_events()
    glfw.swap_buffers(window)

glfw.terminate()
