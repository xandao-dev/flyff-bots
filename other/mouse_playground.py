import math
import numpy as np
import pytweening
from time import sleep
from random import uniform, random
import win32api, win32con


def isNumeric(val):
    return isinstance(val, (float, int, np.int32, np.int64, np.float32, np.float64))


def isListOfPoints(l):
    if not isinstance(l, list):
        return False
    try:
        isPoint = lambda p: ((len(p) == 2) and isNumeric(p[0]) and isNumeric(p[1]))
        return all(map(isPoint, l))
    except (KeyError, TypeError) as e:
        return False


class BezierCurve:
    @staticmethod
    def binomial(n, k):
        """Returns the binomial coefficient "n choose k" """
        return math.factorial(n) / float(math.factorial(k) * math.factorial(n - k))

    @staticmethod
    def bernsteinPolynomialPoint(x, i, n):
        """Calculate the i-th component of a bernstein polynomial of degree n"""
        return BezierCurve.binomial(n, i) * (x**i) * ((1 - x) ** (n - i))

    @staticmethod
    def bernsteinPolynomial(points):
        """
        Given list of control points, returns a function, which given a point [0,1] returns
        a point in the bezier curve described by these points
        """

        def bern(t):
            n = len(points) - 1
            x = y = 0
            for i, point in enumerate(points):
                bern = BezierCurve.bernsteinPolynomialPoint(t, i, n)
                x += point[0] * bern
                y += point[1] * bern
            return x, y

        return bern

    @staticmethod
    def curvePoints(n, points):
        """
        Given list of control points, returns n points in the bezier curve,
        described by these points
        """
        curvePoints = []
        bernstein_polynomial = BezierCurve.bernsteinPolynomial(points)
        for i in range(n):
            t = i / (n - 1)
            curvePoints += (bernstein_polynomial(t),)
        return curvePoints


class HumanCurve:
    """
    Generates a human-like mouse curve starting at given source point,
    and finishing in a given destination point
    """

    def __init__(self, fromPoint, toPoint, **kwargs):
        self.fromPoint = fromPoint
        self.toPoint = toPoint
        self.points = self.generateCurve(**kwargs)

    def generateCurve(self, **kwargs):
        """
        Generates a curve according to the parameters specified below.
        You can override any of the below parameters. If no parameter is
        passed, the default value is used.
        """
        offsetBoundaryX = kwargs.get("offsetBoundaryX", 100)
        offsetBoundaryY = kwargs.get("offsetBoundaryY", 100)
        leftBoundary = kwargs.get("leftBoundary", min(self.fromPoint[0], self.toPoint[0])) - offsetBoundaryX
        rightBoundary = kwargs.get("rightBoundary", max(self.fromPoint[0], self.toPoint[0])) + offsetBoundaryX
        downBoundary = kwargs.get("downBoundary", min(self.fromPoint[1], self.toPoint[1])) - offsetBoundaryY
        upBoundary = kwargs.get("upBoundary", max(self.fromPoint[1], self.toPoint[1])) + offsetBoundaryY
        knotsCount = kwargs.get("knotsCount", 2)
        distortionMean = kwargs.get("distortionMean", 1)
        distortionStdev = kwargs.get("distortionStdev", 1)
        distortionFrequency = kwargs.get("distortionFrequency", 0.25)
        tween = kwargs.get("tweening", pytweening.easeOutQuad)
        targetPoints = kwargs.get("targetPoints", 100)

        internalKnots = self.generateInternalKnots(
            int(round(leftBoundary)),
            int(round(rightBoundary)),
            int(round(downBoundary)),
            int(round(upBoundary)),
            int(round(knotsCount)),
        )
        points = self.generatePoints(internalKnots)
        points = self.distortPoints(points, distortionMean, distortionStdev, distortionFrequency)
        points = self.tweenPoints(points, tween, targetPoints)
        return points

    def generateInternalKnots(self, leftBoundary, rightBoundary, downBoundary, upBoundary, knotsCount):
        """
        Generates the internal knots used during generation of bezier curvePoints
        or any interpolation function. The points are taken at random from
        a surface delimited by given boundaries.
        Exactly knotsCount internal knots are randomly generated.
        """

        if not (
            isNumeric(leftBoundary) and isNumeric(rightBoundary) and isNumeric(downBoundary) and isNumeric(upBoundary)
        ):
            raise ValueError("Boundaries must be numeric")
        if not isinstance(knotsCount, int) or knotsCount < 0:
            raise ValueError("knotsCount must be non-negative integer")
        if leftBoundary > rightBoundary:
            raise ValueError("leftBoundary must be less than or equal to rightBoundary")
        if downBoundary > upBoundary:
            raise ValueError("downBoundary must be less than or equal to upBoundary")

        knotsX = np.random.choice(range(leftBoundary, rightBoundary), size=knotsCount)
        knotsY = np.random.choice(range(downBoundary, upBoundary), size=knotsCount)
        knots = list(zip(knotsX, knotsY))
        return knots

    def generatePoints(self, knots):
        """
        Generates bezier curve points on a curve, according to the internal
        knots passed as parameter.
        """
        if not isListOfPoints(knots):
            raise ValueError("knots must be valid list of points")

        midPtsCnt = max(abs(self.fromPoint[0] - self.toPoint[0]), abs(self.fromPoint[1] - self.toPoint[1]), 2)
        knots = [self.fromPoint] + knots + [self.toPoint]
        return BezierCurve.curvePoints(midPtsCnt, knots)

    def distortPoints(self, points, distortionMean, distortionStdev, distortionFrequency):
        """
        Distorts the curve described by (x,y) points, so that the curve is
        not ideally smooth.
        Distortion happens by randomly, according to normal distribution,
        adding an offset to some of the points.
        """
        if not (isNumeric(distortionMean) and isNumeric(distortionStdev) and isNumeric(distortionFrequency)):
            raise ValueError("Distortions must be numeric")
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not (0 <= distortionFrequency <= 1):
            raise ValueError("distortionFrequency must be in range [0,1]")

        distorted = []
        for i in range(1, len(points) - 1):
            x, y = points[i]
            delta = np.random.normal(distortionMean, distortionStdev) if random() < distortionFrequency else 0
            distorted += ((x, y + delta),)
        distorted = [points[0]] + distorted + [points[-1]]
        return distorted

    def tweenPoints(self, points, tween, targetPoints):
        """
        Chooses a number of points(targetPoints) from the list(points)
        according to tweening function(tween).
        This function in fact controls the velocity of mouse movement
        """
        if not isListOfPoints(points):
            raise ValueError("points must be valid list of points")
        if not isinstance(targetPoints, int) or targetPoints < 2:
            raise ValueError("targetPoints must be an integer greater or equal to 2")

        # tween is a function that takes a float 0..1 and returns a float 0..1
        res = []
        for i in range(targetPoints):
            index = int(tween(float(i) / (targetPoints - 1)) * (len(points) - 1))
            res += (points[index],)
        return res


class HumanMouse:
    def move(self, to_point, duration=0.5, like_robot=False):
        """
        Move mouse from current mouse position to a given point, in a human way or like a robot.
        :param to_point: tuple (x, y)
        :param duration: float. Time in seconds for the movement.
        :param like_robot: bool.
        """

        if like_robot:
            win32api.SetCursorPos(to_point)
            sleep(0.05)
            return

        from_point = win32api.GetCursorPos()
        human_curve = HumanCurve(from_point, to_point, targetPoints=25)
        for point in human_curve.points:
            win32api.SetCursorPos((int(round(point[0])), int(round(point[1]))))
            sleep(round(duration / len(human_curve.points), 3))

    def left_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))

    def double_left_click(self):
        self.left_click()
        self.left_click()

    def right_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))

    def double_right_click(self):
        self.right_click()
        self.right_click()

    def scroll(self, direction):
        """
        Scroll mouse wheel.
        :param direction: str. 'up' or 'down'.
        """
        if direction == "up":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, 120)
        elif direction == "down":
            win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, -120)
        sleep(round(uniform(0.010, 0.025), 4))

    def drag_left_click(self, to_point, duration=0.5, like_robot=False):
        """
        Drag mouse from current mouse position to a given point, in a human way or like a robot.
        :param to_point: tuple (x, y)
        :param duration: float. Time in seconds for the movement.
        :param like_robot: bool.
        """
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))
        self.move(to_point, duration, like_robot)
        sleep(round(uniform(0.015, 0.03), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))

    def drag_right_click(self, to_point, duration=0.5, like_robot=False):
        """
        Drag mouse from current mouse position to a given point, in a human way or like a robot.
        :param to_point: tuple (x, y)
        :param duration: float. Time in seconds for the movement.
        :param like_robot: bool.
        """
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))
        self.move(to_point, duration, like_robot)
        sleep(round(uniform(0.015, 0.03), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        sleep(round(uniform(0.015, 0.03), 4))


if __name__ == "__main__":
    mouse = HumanMouse()
    pass
