## @package main
# Main file
# @author Raffael Siqueira

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

##Class to extends Polygon class given in geometry.py
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

##Class of the moving line used when the user draw the polygon
class Line:
	def __init__(self, pointA):
		self.pointA = pointA
		self.pointB = Point(pointA.x, pointA.y,0)

lineAux = Line(Point(0,0,0))
actualLines = []

## Function to do the correct reshape of the window
# @param w - Width of the window
# @param h - Height of the window

def myReshape(w, h):
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

## Check orientation between 3 points
# @param 3 points that will have their orientation calculated
def orientation(p, q, r):
	o = ((q.y - p.y)*(r.x - q.x)) - ((q.x - p.x) * (r.y - q.y))

	if o == 0:
		return 0

	elif(o>0):
		return 1

	else:
		return 2

## Check if two lines have intersection
#@param l1 Line
# @param l2 Line
# @return boolean
def doIntersect(l1, l2):
	o1 = orientation(l1.pointA, l1.pointB, l2.pointA)
	o2 = orientation(l1.pointA, l1.pointB, l2.pointB)
	o3 = orientation(l2.pointA, l2.pointB, l1.pointA)
	o4 = orientation(l2.pointA, l2.pointB, l1.pointB)

	if o1 != o2 and o3 != o4:
		return True
	else:
		return False

## checks if the user has pressed a keyboard button
# @param Key - The key pressed
# @param x
# @param y
def myKeyboardFunc(Key, x ,y):
	if Key == 'h':
		print 'How to use:'
		print 'Draw polygons with the mouse click'
		print 'Create nails between polygons by right-clicking'
		print 'To delete a nail click on it with the right button'


## Move the line used during the draw
# @param x
# @param y
def mouseDrag(x, y):
	if(clicked):
		lineAux.pointB.x = x
		lineAux.pointB.y = y
	glutPostRedisplay()

## Get clicks on mouse
# @param button
# @param state
# @param x
# @param y
def getMouse(button, state, x, y):
	global activePolygon
	global allPoints
	global clicked
	global lineAux
	global actualPoint
	global selectedPoly
	global dragStart
	if state == GLUT_UP:
		selectedPoly = None

	actualPoint = Point(x,y,0)

	if (button == GLUT_LEFT_BUTTON and state == GLUT_DOWN):
		if len(actualLines) == 0 and lineAux.pointA.x == 0 and lineAux.pointA.y == 0:
			for poly in allPolygons:
				if poly.contains(actualPoint):
					selectedPoly = poly
					break
			if selectedPoly:
				dragStart = actualPoint
				return

		if len(actualLines) == 0 and lineAux.pointA.x != lineAux.pointB.x and lineAux.pointA.y != lineAux.pointB.y:
			actualLines.append(lineAux)
		else:
			if len(actualLines) > 0:
				for i,line in enumerate(actualLines):
					if i != len(actualLines)-1:
						if doIntersect(line, lineAux) and i!=0:
							raise ValueError('Self intersections is not allowed')
						elif doIntersect(line, lineAux) and i==0:
							if line.pointA.dist(lineAux.pointB) >= 20:
								raise ValueError('Self intersections is not allowed')
							lineAux.pointB.x = line.pointA.x + 1
							lineAux.pointB.y = line.pointA.y + 1
							actualPoint.x = line.pointA.x + 1
							actualPoint.y = line.pointA.y + 1
				actualLines.append(lineAux)
				
			
		clicked = True
		lineAux = Line(actualPoint)
		activePolygon.append(actualPoint)
		allPoints.append(actualPoint)

		if len(activePolygon) > 2 and activePolygon[-1].dist(activePolygon[0]) <= 20:
			del allPoints[-1]
			clicked = False
			actualLines.append(lineAux)
			lineAux = Line(Point(0,0,0))
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
					if removeNail in nails:
						nails.remove(removeNail)
					for child in children:
						if child in parent.children:
							parent.children.remove(child)
						if parent in child.parents:
							child.parents.remove(parent)
						if removeNail in child.nails:
							child.nails.remove(removeNail)
				else:
					nails.append(nail)
					parent.children += children
					for child in children:
						if not child.parents:
							child.parents.append(parent)
						if not child.nails:
							child.nails.append(nail)
		

## Rotate the clicked polygon
# @param point
def polyRotate(point):
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
	applyPointsTransformation(selectedPoly, matrix)
	if(selectedPoly.children):
		applyTransformation(selectedPoly, matrix)
	dragStart = point

## Translate the clicked polygon
# @param polygon
# @param point
def polyTranslate(polygon, point):
	global dragStart
	distX = point.x - dragStart.x
	distY = point.y - dragStart.y
	matrix = translate(distX,distY,0)
	if(polygon.children):
		applyTransformation(polygon, matrix)
	applyPointsTransformation(polygon, matrix)
	dragStart = point

## Apply the transformation in the clicked polygon
# @param polygon
# @param matrix
def applyTransformation(polygon,matrix):
	for child in set(polygon.children):
		applyPointsTransformation(child,matrix)
		if(child.children):
			applyTransformation(child,matrix)


## Apply transformation in points
# @param polygon
# @param matrix
def applyPointsTransformation(polygon,matrix):
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

## Function to move polygons
# @param x
# @param y
def mouseMotion(x,y):
	global dragStart
	point = Point(x,y,0)
	if(selectedPoly is not None):
		if selectedPoly.parents and len(selectedPoly.nails) >= 1:
			polyRotate(point)
		elif not selectedPoly.parents:
			polyTranslate(selectedPoly, point)

## Draw the lines when draw polygons
def drawLineAuxs():
	glLineWidth(1.5)
	glBegin(GL_LINES)
	for i in range(1, len(activePolygon)):
		glColor3f(0, 0, 0)
		glVertex3f(activePolygon[i-1].x, activePolygon[i-1].y, 0.0)
		glVertex3f(activePolygon[i].x, activePolygon[i].y, 0.0)
	glEnd()
	glLineWidth(1.5)
	glBegin(GL_LINES)
	glColor3f(0, 0, 0)
	glVertex3f(lineAux.pointA.x, lineAux.pointA.y, 0.0)
	glVertex3f(lineAux.pointB.x, lineAux.pointB.y, 0.0)
	glEnd()

## Draw polygons
def drawPolygon(polygon):
	tess = tessellate(polygon)
	glCallList(tess)

## Draw nails
def drawNails(polygon):
	glPointSize(10.0)
	glBegin(GL_POINTS)
	for nail in polygon.nails:
		glColor3f(0,0,0)
		glVertex3f(nail.x, nail.y, 0.0)
	glEnd()

## Function to render the scene
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
	drawLineAuxs()
	glPopMatrix()
	glutSwapBuffers()
	glutPostRedisplay()
	glFlush()
	
## Main function
def main():
	glutInit(sys.argv)
	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA)
	glutInitWindowPosition(100,100)
	glutInitWindowSize(screenW,screenH)
	glutCreateWindow("Trabalho 2 - CG 2017.2 - Raffael Siqueira")
	glClearColor(255.0,255.0,255.0,0.0)
	glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
	glutSwapBuffers()
	glutKeyboardFunc(myKeyboardFunc)
	glutMouseFunc(getMouse)
	glutMotionFunc(mouseMotion)
	glutPassiveMotionFunc(mouseDrag)
	glutDisplayFunc(renderScene)
	glutIdleFunc(renderScene)
	glutReshapeFunc(myReshape)
	glutMainLoop()

			

if __name__ == '__main__': 
	print 'Press H for help'
	main()