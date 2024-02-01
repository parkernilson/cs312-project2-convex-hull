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
from enum import Enum

# Some global color constants that might be useful
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Global variable that controls the speed of the recursion automation, in seconds
PAUSE = 0.25


class Direction(Enum):
    CW = 0
    CCW = 1


class Side(Enum):
    LEFT = 0
    RIGHT = 1


class Tangent(Enum):
    UPPER = 0
    LOWER = 1


class HullNode:
    def __init__(self, point: QPointF, cw=None, ccw=None):
        self.point = point
        self.cw = cw
        self.ccw = ccw
    
    def __hash__(self):
        return hash((self.point.x(), self.point.y()))
    
    def __str__(self):
        return f"HullNode({round(self.point.x(), 2)}, {round(self.point.y(), 2)})"


class HullEdge:
    def __init__(self, n1: HullNode, n2: HullNode):
        self.n1 = n1
        self.n2 = n2
        self.line = QLineF(n1.point, n2.point)
        self.slope = self.line.dy() / abs(self.line.dx())

    def set_n1(self, n1: HullNode):
        self.n1 = n1
        self.line = QLineF(n1.point, self.n2.point)
        self.slope = self.line.dy() / abs(self.line.dx())

    def set_n2(self, n2: HullNode):
        self.n2 = n2
        self.line = QLineF(self.n1.point, n2.point)
        self.slope = self.line.dy() / abs(self.line.dx())


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

    def coords(self, point: QPointF):
        return (point.x(), point.y())

    def slope_to(self, p1: QPointF, p2: QPointF) -> float:
        line = QLineF(p1, p2)
        return line.dy() / abs(line.dx()) if line.dx() != 0 else float("inf")

    def node_slope_to(self, n1: HullNode, n2: HullNode) -> float:
        line = QLineF(n1.point, n2.point)
        return line.dy() / abs(line.dx()) if line.dx() != 0 else float("inf")

    def sorted_points_cw(
        self, reference: QPointF, points: list[QPointF], reference_side: Side
    ):
        """
        Sorts the given points by slope to the reference point, in the given direction.
        If the direction is clockwise, the points will be sorted as follows:
        If direction is clockwise:
        [reference, ...sorted by increasing slope]
        If direction is counterclockwise:
        [reference, ...sorted by increasing slope]
        """
        without_reference = [point for point in points if point != reference]
        sorted_list = sorted(without_reference, key=lambda point: self.slope_to(reference, point), reverse=reference_side == Side.LEFT)
        return [reference] + sorted_list

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

    def find_hull_extreme(self, hull_node: HullNode, side: Side):
        extreme = hull_node
        visited = set()
        cur_node = hull_node
        while cur_node not in visited:
            visited.add(cur_node)
            if side == Side.LEFT and cur_node.point.x() < extreme.point.x():
                extreme = cur_node
            if side == Side.RIGHT and cur_node.point.x() > extreme.point.x():
                extreme = cur_node

            if cur_node.cw == None:
                raise Exception("Hull is not a closed loop")
            
            cur_node = cur_node.cw
        return extreme

    def construct_hull_list(self, points: list[QPointF]) -> HullNode:
        """
        Args:
          points - a list of points sorted in clockwise order, starting with either
            the leftmost or rightmost point
        """
        if len(points) == 1:
            return HullNode(points[0])

        first_node = HullNode(points[0])

        prev_node = first_node

        for point in points[1:]:
            cur_node = HullNode(point, ccw=prev_node)
            prev_node.cw = cur_node
            prev_node = cur_node

        prev_node.cw = first_node
        first_node.ccw = prev_node

        return first_node

    def compute_tangent(
        self,
        left_hull_pivot_node: HullNode,
        right_hull_pivot_node: HullNode,
        tangent_side: Tangent,
    ) -> HullEdge:
        tangent_edge = HullEdge(left_hull_pivot_node, right_hull_pivot_node)

        invert = 1 if tangent_side == Tangent.UPPER else -1

        left_point_found = False
        right_point_found = False
        while not left_point_found or not right_point_found:
            while not left_point_found:
                next_node = (
                    tangent_edge.n1.ccw if tangent_side == Tangent.UPPER else tangent_edge.n1.cw
                )
                if invert * self.node_slope_to(next_node, tangent_edge.n2) < invert * tangent_edge.slope:
                    tangent_edge.set_n1(next_node)
                else:
                    left_point_found = True

            next_right_node = (
                tangent_edge.n2.cw if tangent_side == Tangent.UPPER else tangent_edge.n2.ccw
            )
            if invert * self.node_slope_to(tangent_edge.n1, next_right_node) > invert * tangent_edge.slope:
                right_point_found = False

            while not right_point_found:
                next_node = (
                    tangent_edge.n2.cw if tangent_side == Tangent.UPPER else tangent_edge.n2.ccw
                )
                if invert * self.node_slope_to(tangent_edge.n1, next_node) > invert * tangent_edge.slope:
                    tangent_edge.set_n2(next_node)
                else:
                    right_point_found = True

            next_left_node = (
                tangent_edge.n1.ccw if tangent_side == Tangent.UPPER else tangent_edge.n1.cw
            )
            if invert * self.node_slope_to(next_left_node, tangent_edge.n2) < invert * tangent_edge.slope:
                left_point_found = False

        return tangent_edge

    def _compute_hull(self, points: list[QPointF], side: Side) -> HullNode:
        """
        Returns a node in a linked list which represents a convex hull.
        The node returned by this function is the furthest node on the opposite side of the hull that is
        being calculated (i.e. if this is a left hull, the rightmost node will be returned) so that
        the node can be used as the pivot node for the next hull.
        """
        if len(points) < 4:
            # base case: return a list of the points sorted by slope when a line
            # 	is made between it and the leftmost point
            extreme = self.find_extreme(points, side)
            points_sorted_cw = self.sorted_points_cw(extreme, points, side)
            reference_node = self.construct_hull_list(points_sorted_cw)
            pivot_node = self.find_hull_extreme(reference_node, Side.LEFT if side == Side.RIGHT else Side.RIGHT)
            return pivot_node

        # split into two hulls
        left_points = points[: len(points) // 2]
        left_hull_pivot_node = self._compute_hull(left_points, Side.LEFT)
        right_points = points[len(points) // 2 : len(points)]
        right_hull_pivot_node = self._compute_hull(right_points, Side.RIGHT)

        # combine the two hulls:

        # find the upper and lower tangents
        upper_tangent = self.compute_tangent(
            left_hull_pivot_node, right_hull_pivot_node, Tangent.UPPER
        )
        lower_tangent = self.compute_tangent(
            left_hull_pivot_node, right_hull_pivot_node, Tangent.LOWER
        )

        # reform the hull
        upper_tangent.n1.cw = upper_tangent.n2
        upper_tangent.n2.ccw = upper_tangent.n1
        lower_tangent.n1.ccw = lower_tangent.n2
        lower_tangent.n2.cw = lower_tangent.n1

        # get a node that is guaranteed to be in the new hull
        node_in_new_hull = upper_tangent.n1

        new_pivot_node = self.find_hull_extreme(
            node_in_new_hull, Side.RIGHT if side == Side.LEFT else Side.LEFT
        )
        return new_pivot_node

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

        left_node_of_hull = self._compute_hull(points_by_x, Side.LEFT)
        polygon = []
        visited = set()
        cur_node = left_node_of_hull
        while cur_node not in visited:
            visited.add(cur_node)
            polygon.append(QLineF(cur_node.point, cur_node.cw.point))
            cur_node = cur_node.cw

        t4 = time.time()

        # when passing lines to the display, pass a list of QLineF objects.  Each QLineF
        # object can be created with two QPointF objects corresponding to the endpoints
        self.showHull(polygon, RED)
        self.showText("Time Elapsed (Convex Hull): {:3.3f} sec".format(t4 - t3))
