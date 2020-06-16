from time import sleep
from random import uniform, randint

import win32api, win32con

from human_mouse.HumanCurve import HumanCurve


class HumanMouse:
	def __init__(self):
		self.w = win32api.GetSystemMetrics(0)
		self.h = win32api.GetSystemMetrics(1)
		self.outside_points = ((0, 0), (self.w, 0), (0, self.h), (self.w, self.h), 
							   (round(self.w/2), 0), (0, round(self.h/2)), 
							   (self.w, round(self.h/2)), (round(self.w/2), self.h))

	def move(self, to_point, from_point=None, duration=0.5, human_curve=None):
		if not from_point:
			from_point = win32api.GetCursorPos()
		if not human_curve:
			human_curve = HumanCurve(from_point, to_point, targetPoints=25)

		for point in human_curve.points:
			win32api.SetCursorPos((int(round(point[0])), int(round(point[1]))))
			sleep(round(duration / len(human_curve.points), 3))

	def move_outside_game(self, from_point=None, duration=0.5, human_curve=None):
		if not from_point:
			from_point = win32api.GetCursorPos()
		if not human_curve:
			human_curve = HumanCurve(
				from_point, 
				self.outside_points[randint(0, len(self.outside_points)-1)], 
				targetPoints=25
			)

		for point in human_curve.points:
			win32api.SetCursorPos((int(round(point[0])), int(round(point[1]))))
			sleep(round(duration / len(human_curve.points), 3))

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