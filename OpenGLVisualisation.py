from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy as np
from PyQt5 import QtOpenGL


class MyOpenGlWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initGeometry(self, points=None, edges=None, colors=None):
        if points is not None and edges is not None and colors is not None:
            self.points = np.array(points)
            self.vertVBO = vbo.VBO(np.reshape(self.points, (1, -1)).astype(np.float32))
            self.vertVBO.bind()

           # self.colors = np.array(colors)
           # self.clrVBO = vbo.VBO(np.reshape(self.colors, (1, -1)).astype(np.float32))
           # self.clrVBO.bind()

            self.edges = np.array(edges)
        else:
            self.points = np.array([])
            self.vertVBO = vbo.VBO(np.reshape(self.points, (1, -1)).astype(np.float32))
            self.vertVBO.bind()

            self.colors = np.array([])
            self.clrVBO = vbo.VBO(np.reshape(self.colors, (1, -1)).astype(np.float32))
            self.clrVBO.bind()

            self.edges = np.array([])

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_DEPTH_TEST)

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0
        self.last_x_mouse = None
        self.last_y_mouse = None

        self.zoomFactor = 1.0

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect = w / float(h)

        gluPerspective(45.0, aspect, 1.0, 200.0)

        glMatrixMode(GL_MODELVIEW)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)

    def paintGL(self, coordinates=None):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glPushMatrix()

        glTranslate(0.0, 0.0, -50.0)
        glScale(0.1 * self.zoomFactor, 0.1 * self.zoomFactor, 0.1 * self.zoomFactor)
        glRotate(self.rotX, 1.0, 0.0, 0.0)
        glRotate(self.rotY, 0.0, 1.0, 0.0)
        glRotate(self.rotZ, 0.0, 0.0, 1.0)
        glTranslate(-0.5, -0.5, -0.5)

        glEnableClientState(GL_VERTEX_ARRAY)
       # glEnableClientState(GL_COLOR_ARRAY)

        glVertexPointer(3, GL_FLOAT, 0, self.vertVBO)
       # glColorPointer(3, GL_FLOAT, 0, self.clrVBO)

        glDrawElements(GL_QUADS, len(self.edges), GL_UNSIGNED_INT, self.edges)

        glDisableClientState(GL_VERTEX_ARRAY)
       # glDisableClientState(GL_COLOR_ARRAY)

        glPopMatrix()

    def wheelEvent(self, event):
        scroll = event.angleDelta()
        if scroll.y() > 0:
            self.zoomFactor += 0.1
        else:
            self.zoomFactor -= 0.1

    def mouseMoveEvent(self, event):
        self.rotY += (event.x() - self.last_x_mouse) / 2
        self.rotX += (event.y() - self.last_y_mouse) / 2
        self.last_y_mouse = event.y()
        self.last_x_mouse = event.x()

    def mouseReleaseEvent(self, event):
        self.last_x_mouse = None
        self.last_y_mouse = None

    def mousePressEvent(self, event):
        self.last_x_mouse = event.x()
        self.last_y_mouse = event.y()
