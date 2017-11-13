from __future__ import division
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
import sys
import random
import numpy
from geometry import *
from tessellator import *
from matrix import *


screenW = 640 
screenH = 480

class myPolygon(Polygon):
	def __init__(self, points, r, g, b):
		super(myPolygon, self).__init__(points)
		self.r = r
		self.g = g
		self.b = b
		self.parents = []
		self.children = []
		self.nails = []

dragStart = Point(0,0,0)

clicked = False
dragging = False
activePolygon = []
allPolygons = []
nails = []
allPoints = []
actualPoint = Point(0,0,0)
currentPoly = []
selectedPoly = None
showHowToUse = True

class Line:
	def __init__(self, pontoA):
		self.pontoA = pontoA
		self.pontoB = Point(pontoA.x, pontoA.y,0)

tempLine = Line(Point(0,0,0))
actualLines = []

def changeSize(w, h):
	global screenW
	global screenH

	if(h == 0):
	       h = 1

	ratio = 1.0* w / h

	glMatrixMode(GL_PROJECTION)
	glLoadIdentity()


	screenW = w
	screenH = h
	glViewport(0, 0, w, h)

def orientation(p, q, r):
	o = ((q.y - p.y)*(r.x - q.x)) - ((q.x - p.x) * (r.y - q.y))

	if o == 0:
		return 0

	elif(o>0):
		return 1

	else:
		return 2

def doIntersect(l1, l2):
	o1 = orientation(l1.pontoA, l1.pontoB, l2.pontoA)
	o2 = orientation(l1.pontoA, l1.pontoB, l2.pontoB)
	o3 = orientation(l2.pontoA, l2.pontoB, l1.pontoA)
	o4 = orientation(l2.pontoA, l2.pontoB, l1.pontoB)

	if o1 != o2 and o3 != o4:
		return True
	else:
		return False


def myKeyboardFunc(Key, x ,y):
	if Key == 'h':
		print 'How to use:'
		print 'Draw polygons with the mouse click'
		print 'Create nails between polygons by right-clicking'
		print 'To delete a nail click on it with the right button'


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
	global selectedPoly
	global dragStart
	if state == GLUT_UP:
		selectedPoly = None

	actualPoint = Point(x,y,0)

	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		if len(actualLines) == 0 and tempLine.pontoA.x == 0 and tempLine.pontoA.y == 0:
			for poly in allPolygons:
				if poly.contains(actualPoint):
					selectedPoly = poly
					break
			if selectedPoly:
				dragStart = actualPoint
				return

		if len(actualLines) == 0 and tempLine.pontoA.x != tempLine.pontoB.x and tempLine.pontoA.y != tempLine.pontoB.y:
			actualLines.append(tempLine)
		else:
			if len(actualLines) > 0:
				for i,line in enumerate(actualLines):
					if i != len(actualLines)-1:
						if doIntersect(line, tempLine) and i!=0:
							raise ValueError('Self intersections is not allowed')
						elif doIntersect(line, tempLine) and i==0:
							if line.pontoA.dist(tempLine.pontoB) >= 20:
								raise ValueError('Self intersections is not allowed')
							tempLine.pontoB.x = line.pontoA.x + 1
							tempLine.pontoB.y = line.pontoA.y + 1
							actualPoint.x = line.pontoA.x + 1
							actualPoint.y = line.pontoA.y + 1
				actualLines.append(tempLine)
				
			
		clicked = True
		tempLine = Line(actualPoint)
		activePolygon.append(actualPoint)
		allPoints.append(actualPoint)

		if len(activePolygon) > 2 and activePolygon[-1].dist(activePolygon[0]) <= 20:
			del allPoints[-1]
			clicked = False
			actualLines.append(tempLine)
			tempLine = Line(Point(0,0,0))
			poly = myPolygon(activePolygon[:], numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0), numpy.random.uniform(0.0, 1.0))
			
				
			tessellate(poly)
			
			allPolygons.append(poly)
			del actualLines[:]
			del activePolygon[:]

	elif (button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN):
		
		firstPolygon = True
		children = []
		parent = None
		removeNail = None
		for nail in nails:
			if nail.dist(actualPoint) <= 20:
				removeNail = nail

		for poly in allPolygons:
			if poly.contains(actualPoint):
				if firstPolygon:
					parent = poly
					nail = actualPoint
					firstPolygon = False
				else:
					children.append(poly)
			if children:
				if removeNail:
					nails.remove(removeNail)
					for child in children:
						parent.children.remove(child)
						child.parents.remove(parent)
						child.nails.remove(removeNail)
				else:
					nails.append(nail)
					parent.children += children
					for child in children:
						child.parents.append(parent)
						child.nails.append(nail)
		

def rotatePolygon(point):
	global dragStart
	rotatePoint = selectedPoly.nails[0]
	 

	startPoint = dragStart - rotatePoint
	anglePoint = point - rotatePoint

	inner_product = startPoint.x*anglePoint.x + startPoint.y*anglePoint.y

	len1 = math.hypot(startPoint.x, startPoint.y)
	len2 = math.hypot(anglePoint.x, anglePoint.y)

	angle = math.acos(inner_product/(len1*len2))

	angle = angle*180/math.pi
	angle = math.copysign(angle, anglePoint.crossProd(startPoint).z)
	angle *= -1

	matrix = translateAndRotate(angle, rotatePoint, Point(0,0,1))
	applyTransformationToPoints(selectedPoly, matrix)
	if(selectedPoly.children):
		applyTransformationToChildren(selectedPoly, matrix)
	dragStart = point

def translatePolygon(polygon, point):
	global dragStart
	distX = point.x - dragStart.x
	distY = point.y - dragStart.y
	matrix = translate(distX,distY,0)
	if(polygon.children):
		applyTransformationToChildren(polygon, matrix)
	applyTransformationToPoints(polygon, matrix)
	dragStart = point

def applyTransformationToChildren(polygon,matrix):
	for child in set(polygon.children):
		applyTransformationToPoints(child,matrix)
		if(child.children):
			applyTransformationToChildren(child,matrix)


def applyTransformationToPoints(polygon,matrix):
	matrix = numpy.array(matrix)
	for p in polygon.points:
		pointN = numpy.array([p.x,p.y,0,1])
		
		result = matrix.dot(pointN)
		p.x = result[0]
		p.y = result[1]

	for nail in polygon.nails:
		pointN = numpy.array([nail.x,nail.y,0,1])
		result = matrix.dot(pointN)
		nail.x = result[0]
		nail.y = result[1]

def mouseMotion(x,y):
	global dragStart
	point = Point(x,y,0)
	if(selectedPoly is not None):
		if(selectedPoly.parents and len(selectedPoly.nails) == 1):
			rotatePolygon(point)
		elif(not selectedPoly.parents):
			translatePolygon(selectedPoly, point)

def drawTempLines():
	glLineWidth(3.0)
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

def drawPolygon(polygon):
	tess = tessellate(polygon)
	glCallList(tess)

def drawNails(polygon):
	glPointSize(10.0)
	glBegin(GL_POINTS)
	for nail in polygon.nails:
		glColor3f(0,0,0)
		glVertex3f(nail.x, nail.y, 0.0)
	glEnd()


def renderScene ():
	global showHowToUse

	if showHowToUse:
		print 'How to use:'
		print 'Draw polygons with the mouse click'
		print 'Create nails between polygons by right-clicking'
		print 'To delete a nail click on it with the right button'
		showHowToUse = False
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glEnable(GL_POINT_SMOOTH)
	glEnable(GL_LINE_SMOOTH)
	glPushMatrix()
	glMatrixMode (GL_PROJECTION)
	gluOrtho2D (0.0, screenW, screenH, 0.0)
	for polygon in allPolygons:
		drawPolygon(polygon)
		drawNails(polygon)
	drawTempLines()
	glPopMatrix()
	glutSwapBuffers()
	glutPostRedisplay()
	glFlush()
	

def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
	glutInitWindowPosition(100,100)
	glutInitWindowSize(screenW,screenH)
	glutCreateWindow("Trabalho 2 - CG 2017.2 - Raffael SIqueira")
	glClearColor(255.0,255.0,255.0,0.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glutSwapBuffers()
	glutKeyboardFunc(myKeyboardFunc)
	glutMouseFunc(getMouse)
	glutMotionFunc(mouseMotion)
	glutPassiveMotionFunc(mouseDrag)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	glutReshapeFunc(changeSize)
	glutMainLoop()

			

if __name__ == '__main__': main()