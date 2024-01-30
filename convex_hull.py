from which_pyqt import PYQT_VER
if PYQT_VER == 'PYQT5':
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT4':
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == 'PYQT6':
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception('Unsupported Version of PyQt: {}'.format(PYQT_VER))



import time

# Some global color constants that might be useful
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25

#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):

# Class constructor
	def __init__( self):
		super().__init__()
		self.pause = False

# Some helper methods that make calls to the GUI, allowing us to send updates
# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self,line,color):
		self.showTangent(line,color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon,color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self,polygon):
		self.view.clearLines(polygon)

	def showText(self,text):
		self.view.displayStatusText(text)

	def __compute_hull(self, points: list[QPointF], left: bool) -> list[QPointF]:
		"""
		Returns a list of points sorted by slope with the leftmost point (if this is a left hull)
		or the rightmost point (if this is a right hull)
		"""
		if len(points) < 4:
			# base case: return a list of the points sorted by slope when a line
			# 	is made between it and the leftmost point

			pass
		
		# split into two hulls
		left_points = points[:len(points)//2]
		left_hull = self.__compute_hull(left_points, True)
		right_points = points[len(points)//2 + 1:len(points)]
		right_hull = self.__compute_hull(right_points, False)

		# left and right hulls are lists of points sorted by their slope from their respective
		# leftmost (left hull) and rightmost (right hull) points
		# 	Therefore, by moving to higher indices in the left hull, you move counterclockwise around the hull
		# 	while by moving to higher indices in the right hull, you move clockwise around the hull

		# combine the two hulls:
		# pick the rightmost point of the left hull
		# pick the leftmost point of the right hull
		# make a line between them 
		# while the slope of the line is decreased (made less positive) keep moving
		# 	the left point counter clockwise around the left hull
		# while the slope of the line is increased (made more positive) keep moving
		# 	the right points clockwise around the right hull
		# keep alternating between the two rotations until the line is unchanged
		# the resulting points form the line which connects the two hulls on top.
		# then, do the same thing but reversed for the bottom line

		# when the combining points are determined, merge the lists and in the process
		# 	remove any points whose slopes are between the newly added connecting points on each
		# 	hull respectively

		# sort the new list of points by slope with the leftmost point (if this is a left hull)
		# 	or with the rightmost point (if this is a right hull)

		# return the list of points

		pass

# This is the method that gets called by the GUI and actually executes
# the finding of the hull
	def compute_hull( self, points: list[QPointF], pause, view):
		self.pause = pause
		self.view = view
		assert( type(points) == list and type(points[0]) == QPointF )

		t1 = time.time()

		points_by_x = sorted(points, key=lambda point: point.x())

		t2 = time.time()

		t3 = time.time()

		hull_points = self.__compute_hull(points, True)
		polygon = [QLineF(points[i],points[i+1]) for i in range(len(points)-1)]

		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon,RED)
		self.showText('Time Elapsed (Convex Hull): {:3.3f} sec'.format(t4-t3))
