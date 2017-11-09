from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import random
import numpy
from geometry import *
from tessellator import *


screenW = 640 
screenH = 480


clicked = False
dragging = False
activePolygon = []
allPolygons = []
allPoints = []
actualPoint = Point(0,0,0)
nails = []

class Line:
	def __init__(self, pontoA):
		self.pontoA = pontoA
		self.pontoB = Point(pontoA.x, pontoA.y,0)

tempLine = Line(Point(0,0,0))

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
	global actualPoint
	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		actualPoint = Point(x,y,0)
		if len(activePolygon) == 0:
			for poly in allPolygons:
				if poly.contains(actualPoint):
					return
		clicked = True
		tempLine = Line(actualPoint)
		activePolygon.append(actualPoint)
		allPoints.append(actualPoint)

		if len(activePolygon) > 2 and activePolygon[-1].dist(activePolygon[0]) <= 10:
			del allPoints[-1]
			activePolygon[-1] = activePolygon[0]
			clicked = False
			tempLine = Line(Point(0,0,0))
			poly = Polygon(activePolygon[:], numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0))
			if(poly.isConvex()):
				print("Convexo")
			print("Adicionou Polygon\n")
			tessellate(poly)
			allPolygons.append(poly)
			del activePolygon[:]

	elif (button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN):
		print('Clique com o botao direito')
		actualPoint = Point(x,y,1)
		nails.append(actualPoint)
		for poly in allPolygons:
			if poly.contains(actualPoint):
				poly.nail = actualPoint
				return


def mouseMotion(x,y):
	firstClick = actualPoint
	dragPoint = Point(x,y,0)
	global dragging
	for poly in allPolygons:
		if poly.contains(dragPoint):
			dragging = True
			distx = dragPoint.x - firstClick.x
			disty = dragPoint.y - firstClick.y
			for point in poly.points:
				point.x = point.x + distx
				point.y = point.y + disty
	glutPostRedisplay()
	dragging = False


def renderScene ():
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, screenW, screenH, 0.0)
	glLineWidth(3.0)
	glColor3f(0,0,0)
	glPointSize(10)
	glBegin(GL_POINTS)
	for nail in nails:
		glVertex3f(nail.x, nail.y, 0)
	glEnd()
	glBegin(GL_LINES)
	for i in range(1, len(activePolygon)):
		glColor3f(0, 0, 0)
		glVertex3f(activePolygon[i-1].x, activePolygon[i-1].y, 0.0)
		glVertex3f(activePolygon[i].x, activePolygon[i].y, 0.0)
	glEnd()
	glLineWidth(3.0)
	glBegin(GL_LINES)
	glColor3f(0, 0, 0)
	glVertex3f(tempLine.pontoA.x, tempLine.pontoA.y, 0.0)
	glVertex3f(tempLine.pontoB.x, tempLine.pontoB.y, 0.0)
	glEnd()
	for polygon in allPolygons:
		global test
		test = tessellate(polygon)
		glCallList(test)
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
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glutSwapBuffers()
	glutMouseFunc(getMouse)
	glutMotionFunc(mouseMotion)
	glutPassiveMotionFunc(mouseDrag)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	glutReshapeFunc(changeSize)
	glutMainLoop()

			

if __name__ == '__main__': main()