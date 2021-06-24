import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from PyQt5.QtWidgets import QOpenGLWidget, QApplication


class MyOpenGlWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.called = False

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClear(GL_COLOR_BUFFER_BIT)

    def resizeGL(self, w, h):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-50, 50, -50, 50, -50.0, 50.0)

        glViewport(0, 0, w, h)

    def paintGL(self, coordinates=None):
        glColor3f(1.0, 0.0, 0.0)
        glRectf(-5, -5, 5, 5)
