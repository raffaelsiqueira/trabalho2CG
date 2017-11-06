from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import random
import numpy
from geometry import *


screenW = 640 
screenH = 480


clicked = False
activePolygon = []
allPolygons = []
allPoints = []
colors = []

class Line:
	def __init__(self, pontoA):
		self.pontoA = pontoA
		self.pontoB = Point(pontoA.x, pontoA.y)

tempLine = Line(Point(0,0))

def changeSize(w, h):
	if(h == 0):
	       h = 1

	ratio = 1.0* w / h

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()

	screenW = w
	screenH = h
	glViewport(0, 0, w, h)

def mouseDrag(x, y):
	if(clicked):
		tempLine.pontoB.x = x
		tempLine.pontoB.y = y
	glutPostRedisplay()

def getMouse(button, state, x, y):
	global activePolygon
	global allPoints
	global clicked
	global tempLine
	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		actualPoint = Point(x,y)
		clicked = True
		tempLine = Line(actualPoint)
		activePolygon.append(actualPoint)
		allPoints.append(actualPoint)

		if len(activePolygon) > 2 and activePolygon[-1].dist(activePolygon[0]) <= 50:
			del allPoints[-1]
			activePolygon[-1] = activePolygon[0]
			clicked = False
			tempLine = Line(Point(0,0))
			poly = Polygon(activePolygon[:], numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0))
			if(poly.isConvex()):
				print("Convexo")
			print("Adicionou Polygon\n")
			allPolygons.append(poly)
			del activePolygon[:]

def renderScene():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, screenW, screenH, 0.0)
	glPointSize(5.0)

	for polygon in allPolygons:
		glBegin(GL_POLYGON)	

		if(False):
			for polygonPoint in polygon.points:
				#glColor3f(0, 0, 255)
				glColor3f(polygon.r, polygon.g, polygon.b)
				glVertex3f(polygonPoint.x, polygonPoint.y, 0)
		else:
			points = polygon
			for polygonPoint in polygon.points:
				glColor3f(polygon.r, polygon.g, polygon.b)
				glVertex3f(polygonPoint[0], polygonPoint[1], 0)
		glEnd()




	glLineWidth(3.0)
	glBegin(GL_LINES)
	for i in range(1, len(activePolygon)):
		glColor3f(0.0, 0.0, 0.0)
		glVertex3f(activePolygon[i-1].x, activePolygon[i-1].y, 0.0)
		glVertex3f(activePolygon[i].x, activePolygon[i].y, 0.0)
	glEnd()

	glLineWidth(3.0)
	glBegin(GL_LINES)
	glColor3f(0.0, 0.0, 0.0)
	glVertex3f(tempLine.pontoA.x, tempLine.pontoA.y, 0.0)
	glVertex3f(tempLine.pontoB.x, tempLine.pontoB.y, 0.0)
	glEnd()


	glPopMatrix()
	glutSwapBuffers()
	glutPostRedisplay()
	glFlush()

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
	glutInitWindowPosition(100,100)
	glutInitWindowSize(screenW,screenH)
	glutCreateWindow("Trabalho 2 - CG")
	glClearColor(255.0,255.0,255.0,0.0)
	glutMouseFunc(getMouse)
	glutPassiveMotionFunc(mouseDrag)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	glutReshapeFunc(changeSize)
	glutMainLoop()

			

if __name__ == '__main__': main()