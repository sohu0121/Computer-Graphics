import glfw
import numpy as np
from OpenGL.GL import *


def render(T):
    glClear(GL_COLOR_BUFFER_BIT)
    glLoadIdentity()

    # draw coordinate
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


def main():
    if not glfw.init():
        return

    window = glfw.create_window(480, 480, "2022007329-2-2", None, None)

    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)

    glfw.swap_interval(1)

    while not glfw.window_should_close(window):
        glfw.poll_events()

        t = glfw.get_time()

        # rotation
        th = t
        T = np.array([[np.cos(th), -np.sin(th), np.cos(th) / 2.], [np.sin(th), np.cos(th), np.sin(th) / 2.], [0., 0., 1.]])

        render(T)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
