import glfw
import numpy as np
from OpenGL.GL import *
import math

TransformationKey = {
    glfw.KEY_Q: 1,
    glfw.KEY_E: 2,
    glfw.KEY_A: 3,
    glfw.KEY_D: 4,
    glfw.KEY_1: 5
}

CurrentKey = 0


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw cooridnate
    glBegin(GL_LINES)
    glColor3ub(255, 0, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([1., 0.]))
    glColor3ub(0, 255, 0)
    glVertex2fv(np.array([0., 0.]))
    glVertex2fv(np.array([0., 1.]))
    glEnd()

    # draw triangle
    glBegin(GL_TRIANGLES)
    glColor3ub(255, 255, 255)
    glVertex2fv((T @ np.array([0., 0.5, 1.]))[:-1])
    glVertex2fv((T @ np.array([0., 0., 1.]))[:-1])
    glVertex2fv((T @ np.array([0.5, 0., 1.]))[:-1])
    glEnd()


def key_callback(window, key, scancode, action, mods):
    global CurrentKey
    if action == glfw.RELEASE:
        CurrentKey = TransformationKey.get(key, 0)


def main():
    if not glfw.init():
        return

    global CurrentKey

    window = glfw.create_window(480, 480, "2022007329-3-1", None, None);

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.set_key_callback(window, key_callback)

    T = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if CurrentKey == 1:
            T = np.array([[1., 0., -0.1], [0., 1., 0], [0., 0., 1.]]) @ T
        elif CurrentKey == 2:
            T = np.array([[1., 0., 0.1], [0., 1., 0], [0., 0., 1.]]) @ T
        elif CurrentKey == 3:
            Radian = 10 * math.pi / 180.
            T = T @ np.array([[math.cos(Radian), -math.sin(Radian), 0.], [math.sin(Radian), math.cos(Radian), 0.], [0., 0., 1.]])
        elif CurrentKey == 4:
            Radian = -10 * math.pi / 180.
            T = T @ np.array(
                [[math.cos(Radian), -math.sin(Radian), 0.], [math.sin(Radian), math.cos(Radian), 0.], [0., 0., 1.]])
        elif CurrentKey == 5:
            T = np.array([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])

        CurrentKey = 0
        render(T)

        glfw.swap_buffers(window)


if __name__ == "__main__":
    main()
