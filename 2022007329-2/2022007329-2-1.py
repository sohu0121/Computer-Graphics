import glfw
import numpy as np
from OpenGL.GL import *
import math

PrimitiveMap = {
    glfw.KEY_1: GL_POINTS,
    glfw.KEY_2: GL_LINES,
    glfw.KEY_3: GL_LINE_STRIP,
    glfw.KEY_4: GL_LINE_LOOP,
    glfw.KEY_5: GL_TRIANGLES,
    glfw.KEY_6: GL_TRIANGLE_STRIP,
    glfw.KEY_7: GL_TRIANGLE_FAN,
    glfw.KEY_8: GL_QUADS,
    glfw.KEY_9: GL_QUAD_STRIP,
    glfw.KEY_0: GL_POLYGON
}

CurrentPrimitive = GL_POINTS


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()
    glBegin(CurrentPrimitive)

    NumSide = 12
    Radian = 2 * math.pi / NumSide;

    R = np.array([[math.cos(Radian), -math.sin(Radian)], [math.sin(Radian), math.cos(Radian)]])

    v = T

    for _ in range(NumSide):
        v = R @ v
        glVertex2fv(v[0], v[1])

    glEnd()


def key_callback(window, key, scancode, action, mods):
    global CurrentPrimitive
    if action == glfw.PRESS:
        if key in PrimitiveMap:
            CurrentPrimitive = PrimitiveMap[key]


def main():
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2022007329-2-1", None, None);

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        T = np.array([[1., 0.], [0., 1.]])

        render(T)

        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
