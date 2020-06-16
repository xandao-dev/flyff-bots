from time import sleep
from random import uniform, randint

import win32api, win32con

from human_mouse.HumanCurve import HumanCurve


class HumanMouse():
	def __init__(self):
		pass

	def move(self, toPoint, duration=1, humanCurve=None):
		fromPoint = win32api.GetCursorPos()
		if not humanCurve:
			humanCurve = HumanCurve(fromPoint, toPoint)

		for point in humanCurve.points:
			win32api.SetCursorPos((int(point[0]), int(point[1])))
			sleep(duration / len(humanCurve.points))

	def move_random_corner(self, duration=0.5, humanCurve=None):
		w = win32api.GetSystemMetrics(0)
		h = win32api.GetSystemMetrics(1)

		corners = ((0, 0), (0, w), (0, h), (w, h))

		fromPoint = win32api.GetCursorPos()
		if not humanCurve:
			humanCurve = HumanCurve(fromPoint, corners[randint(0, 3)])

		for point in humanCurve.points:
			win32api.SetCursorPos((int(point[0]), int(point[1])))
			sleep(duration / len(humanCurve.points))

	def move_like_robot(self, pos, sleep_time=0.05):
		win32api.SetCursorPos(pos)
		sleep(sleep_time)

	def right_click(self, pos=None, set_position=False):
		if set_position and pos:
			win32api.SetCursorPos(pos)
			sleep(round(uniform(0.04, 0.07), 4))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
		sleep(round(uniform(0.010, 0.025), 4))
		win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)