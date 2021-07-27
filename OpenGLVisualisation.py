from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.arrays import vbo
import numpy as np
from PyQt5 import QtOpenGL
from OpenGL.GLUT import *


class MyOpenGlWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initGeometry(self, points=None, colors=None, cube_points=None, cube_edges=None, cube_colors=None,
                     x=0.0, y=0.0, z=0.0):
        if points is not None and colors is not None:
            self.points = np.array(points)
            self.vertVBO = vbo.VBO(np.reshape(self.points, (1, -1)).astype(np.float32))

            self.colors = np.array(colors)
            self.clrVBO = vbo.VBO(np.reshape(self.colors, (1, -1)).astype(np.float32))

            edges = []
            for e in range(0, len(self.points) - 1):
                edges.append(e)
                edges.append(e + 1)
                edges.append(e + 1)
                edges.append(e)
            self.edges = np.array(edges)

            self.points_cube = np.array(cube_points)
            self.vertVBOcube = vbo.VBO(np.reshape(self.points_cube, (1, -1)).astype(np.float32))

            self.colors_cube = np.array(cube_colors)
            self.clrVBOcube = vbo.VBO(np.reshape(self.colors_cube, (1, -1)).astype(np.float32))

            self.edges_cube = np.array(cube_edges)

            self.string = "X: {}mm Y: {}mm Z: {}mm".format(x, y, z)
        else:
            self.points = np.array([])
            self.vertVBO = vbo.VBO(np.reshape(self.points, (1, -1)).astype(np.float32))

            self.colors = np.array([])
            self.clrVBO = vbo.VBO(np.reshape(self.colors, (1, -1)).astype(np.float32))

            self.edges = np.array([])

            self.points_cube = np.array([])
            self.vertVBOcube = vbo.VBO(np.reshape(self.points_cube, (1, -1)).astype(np.float32))

            self.colors_cube = np.array([])
            self.clrVBOcube = vbo.VBO(np.reshape(self.colors_cube, (1, -1)).astype(np.float32))

            self.edges_cube = np.array([])

            self.string = "X: 0mm Y: 0mm Z: 0mm"

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glEnable(GL_DEPTH_TEST)
        glutInit()

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
        glClearColor(43.0/255.0, 62.0/255.0, 70.0/255.0, 1.0)

        glPushMatrix()

        glTranslate(0.0, 0.0, -50.0)

        glScale(0.1, 0.1, 0.1)
        glRotate(0.0, 1.0, 0.0, 0.0)
        glRotate(0.0, 0.0, 1.0, 0.0)
        glRotate(0.0, 0.0, 0.0, 1.0)

        glColor3f(1.0, 1.0, 1.0)

        glPushAttrib(GL_VIEWPORT)

        glViewport(0, 0, 50, 50)

        glRasterPos2f(10, 10)

        for i in range(len(self.string)):
           glutBitmapCharacter(GLUT_BITMAP_8_BY_13, ord(self.string[i]))

        glPopAttrib()

        glScale(1.0 * self.zoomFactor, 1.0 * self.zoomFactor, 1.0 * self.zoomFactor)
        glRotate(self.rotX, 1.0, 0.0, 0.0)
        glRotate(self.rotY, 0.0, 1.0, 0.0)
        glRotate(self.rotZ, 0.0, 0.0, 1.0)

        glEnableClientState(GL_VERTEX_ARRAY)
        glEnableClientState(GL_COLOR_ARRAY)

        self.vertVBO.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)

        self.clrVBO.bind()
        glColorPointer(3, GL_FLOAT, 0, None)

        glDrawElements(GL_QUADS, len(self.edges), GL_UNSIGNED_INT, self.edges)

        self.vertVBOcube.bind()
        glVertexPointer(3, GL_FLOAT, 0, None)

        self.clrVBOcube.bind()
        glColorPointer(3, GL_FLOAT, 0, None)

        glDrawElements(GL_QUADS, len(self.edges_cube), GL_UNSIGNED_INT, self.edges_cube)

        glDisableClientState(GL_VERTEX_ARRAY)
        glDisableClientState(GL_COLOR_ARRAY)

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
