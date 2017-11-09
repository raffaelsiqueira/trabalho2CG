from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

aux = []

def tessErrorCB(errorCode):
    errorStr = gluErrorString(errorCode)
    print("[ERROR]: " + errorStr)

def tessellate(polygon):
    global aux
    Id = glGenLists(1)
    if not Id:
        return Id
    tess = gluNewTess()
    if not tess:
        return 0
    gluTessCallback(tess, GLU_TESS_BEGIN, glBegin)
    gluTessCallback(tess, GLU_TESS_END, glEnd)
    gluTessCallback(tess, GLU_TESS_ERROR, tessErrorCB)
    gluTessCallback(tess, GLU_TESS_VERTEX, glVertex3dv)

    glNewList(Id, GL_COMPILE)
    glColor3f(polygon.r, polygon.g, polygon.b)
    gluTessBeginPolygon(tess, 0)         
    gluTessBeginContour(tess)
    for vertex in polygon.points:
        aux = [vertex.x, vertex.y, vertex.z]
        gluTessVertex(tess, aux, aux)
    gluTessEndContour(tess)
    gluTessEndPolygon(tess)
    glEndList()
    gluDeleteTess(tess)

    return Id
