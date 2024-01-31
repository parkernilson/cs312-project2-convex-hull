from enum import Enum

from which_pyqt import PYQT_VER

if PYQT_VER == "PYQT5":
	from PyQt5.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == "PYQT4":
	from PyQt4.QtCore import QLineF, QPointF, QObject
elif PYQT_VER == "PYQT6":
	from PyQt6.QtCore import QLineF, QPointF, QObject
else:
	raise Exception("Unsupported Version of PyQt: {}".format(PYQT_VER))


import time

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


class Side(Enum):
	LEFT = 0
	RIGHT = 1


class Dir(Enum):
	CW = 0
	CCW = 1


#
# This is the class you have to complete.
#
class ConvexHullSolver(QObject):
	# Class constructor
	def __init__(self):
		super().__init__()
		self.pause = False

	# Some helper methods that make calls to the GUI, allowing us to send updates
	# to be displayed.

	def showTangent(self, line, color):
		self.view.addLines(line, color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseTangent(self, line):
		self.view.clearLines(line)

	def blinkTangent(self, line, color):
		self.showTangent(line, color)
		self.eraseTangent(line)

	def showHull(self, polygon, color):
		self.view.addLines(polygon, color)
		if self.pause:
			time.sleep(PAUSE)

	def eraseHull(self, polygon):
		self.view.clearLines(polygon)

	def showText(self, text):
		self.view.displayStatusText(text)

	def sort_points_by_slope(
		self, reference: QPointF, points: list[QPointF]
	):
		"""
		Sorts the given points by slope to the reference point, in the given direction.
		If the direction is clockwise, the points will be sorted as follows:
		If direction is clockwise:
		[reference, ...sorted by increasing slope]
		If direction is counterclockwise:
		[reference, ...sorted by increasing slope]
		"""
		slopes = {
			point: QLineF(reference, point).dy() / QLineF(reference, point).dx()
			if point != reference
			else -float("inf") 
			for point in points
		}

		return sorted(points, key=lambda point: slopes[point])

	def find_extreme(self, points: list[QPointF], side: Side):
		"""
		If left, then returns the leftmost point. If not left (right) then returns the rightmost point.
		"""
		extreme = points[0]
		for point in points[1:]:
			if side == Side.RIGHT and point.x() > extreme.x():
				extreme = point
			elif side == Side.LEFT and point.x() < extreme.x():
				extreme = point
		return extreme

	def get_next_point(
		self, points: list[QPointF], index: int, sorted: Dir, move_dir: Dir
	) -> tuple[QPointF, int]:
		"""
		Returns a tuple (point, new_index) with the next point in the given direction
		"""
		next_index = index
		# if sorted clockwise, increase index for clockwise
		# if sorted clockwise, decrease index for ccw
		if sorted == Dir.CW:
			next_index += 1 if move_dir == Dir.CW else -1
		# if sorted ccw, increase index for ccw
		# if sorted ccw, decrease index for clockwise
		elif sorted == Dir.CCW:
			next_index += 1 if move_dir == Dir.CCW else -1
		
		return next_index % len(points)

	def _compute_hull(self, points: list[QPointF], side: Side) -> list[QPointF]:
		"""
		Returns a list of points sorted by slope with the leftmost point (if this is a left hull)
		or the rightmost point (if this is a right hull)
		"""
		if len(points) < 4:
			# base case: return a list of the points sorted by slope when a line
			# 	is made between it and the leftmost point
			extreme = self.find_extreme(points, side)
			return self.sort_points_by_slope(extreme, points)

		# split into two hulls
		left_points = points[: len(points) // 2]
		left_hull = self._compute_hull(left_points, Side.LEFT)
		right_points = points[len(points) // 2 : len(points)]
		right_hull = self._compute_hull(right_points, Side.RIGHT)

		# left and right hulls are lists of points sorted by their slope from their respective
		# leftmost (left hull) and rightmost (right hull) points
		# 	Therefore, by moving to higher indices in the left hull, you move counterclockwise around the hull
		# 	while by moving to higher indices in the right hull, you move clockwise around the hull

		# combine the two hulls:
		# pick the rightmost point of the left hull
		left_pivot = self.find_extreme(left_points, Side.RIGHT)
		# pick the leftmost point of the right hull
		right_pivot = self.find_extreme(right_points, Side.LEFT)
		# make a line between them
		# TODO: copy the points by value, not by reference
		upper_edge = QLineF(left_pivot, right_pivot)
		lower_edge = QLineF(left_pivot, right_pivot)

		# while the slope of the line is decreased (made less positive) keep moving
		# 	the left point counter clockwise around the left hull
		# while the slope of the line is increased (made more positive) keep moving
		# 	the right points clockwise around the right hull
		# keep alternating between the two rotations until the line is unchanged
		# the resulting points form the line which connects the two hulls on top.
		# then, do the same thing but reversed for the bottom line
		left_point_found = False
		right_point_found = False
		while not left_point_found or not right_point_found:
			# left_index = get the left index from the find_extreme method
			while not left_point_found:
				# rotate counter clockwise until doing so yields a lesser slope
				next_point = self.get_next_point(left_points, )
				# set left_point_found
				pass
			# if moving the right point clockwise would yield a lesser slope, set right_point_found to false
			while not right_point_found:
				# rotate clockwise until doing so yields a greater slope
				# set right_point_found
				pass
			# if moving the left point counter clockwise would yield a greater slope, set left_point_found to False

		# do the same as above for the lower edge (but reversed)
		left_point_found = False
		right_point_found = False
		while not left_point_found or not right_point_found:
			while not left_point_found:
				pass
			while not right_point_found:
				pass

		# when the combining points are determined, merge the lists and in the process
		# 	remove any points whose slopes are between the newly added connecting points on each
		# 	hull respectively
		# i.e. on the left hull:
		# 	any points that have a slope < p0 of upper_edge and slope > p0 of lower_edge should be filtered out
		# on the right hull:
		# 	any points that have -slope < p0 of upper and -slope > p0 of lower
		# TODO: implement this
		# if the side is left, reverse the right points (to get same orientation)
		# if the side is right, reverse the left points (to get same orientation)
		left_most_point = left_points[0]
		right_most_point = right_points[0]
		if side == Side.LEFT:
			right_points.reverse()
		elif side == Side.RIGHT:
			left_points.reverse()
		extreme_point = left_most_point if side == Side.LEFT else right_most_point
		left_slopes = { point: QLineF(extreme_point, point).dy() / QLineF(extreme_point, point).dy() for point in left_points }
		right_slopes = { point: QLineF(extreme_point, point).dy() / QLineF(extreme_point, point).dy() for point in right_points }

		# TODO: make sure the extreme point is at the beginning of this list
		new_points = [
			point for point in left_points
			if left_slopes[point] < left_slopes[upper_edge.p1()] and left_slopes[point] > left_slopes[lower_edge.p1()]
		].extend([
			point for point in right_points
			if right_slopes[point] < right_slopes[upper_edge.p2()] and right_slopes[point] > right_slopes[lower_edge.p2()]
		])

		return new_points

	# This is the method that gets called by the GUI and actually executes
	# the finding of the hull
	def compute_hull(self, points: list[QPointF], pause, view):
		self.pause = pause
		self.view = view
		assert type(points) == list and type(points[0]) == QPointF

		t1 = time.time()

		points_by_x = sorted(points, key=lambda point: point.x())

		t2 = time.time()

		t3 = time.time()

		hull_points = self._compute_hull(points, Side.LEFT)
		polygon = [QLineF(points[i], points[i + 1]) for i in range(len(points) - 1)]

		t4 = time.time()

		# when passing lines to the display, pass a list of QLineF objects.  Each QLineF
		# object can be created with two QPointF objects corresponding to the endpoints
		self.showHull(polygon, RED)
		self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))
