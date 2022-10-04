from time import sleep
from random import uniform, randint

import win32api, win32con, win32gui

from libs.human_mouse.HumanCurve import HumanCurve


class HumanMouse:
    def __init__(self, hwnd):
        self.hwnd = hwnd
        self.window_rect = win32gui.GetWindowRect(self.hwnd)

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

    def move_outside_game(self, duration=0.5, like_robot=False):
        """
        Move mouse outside the game window.
        :param duration: float. Time in seconds for the movement.
        :param like_robot: bool.
        """
        self.move(self.__get_random_outside_point(), duration, like_robot)

    def right_click(self, pos=None, set_position=False):
        if set_position and pos:
            win32api.SetCursorPos(pos)
            sleep(round(uniform(0.04, 0.07), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
        sleep(round(uniform(0.010, 0.025), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)

    def left_click(self, pos=None, set_position=False):
        if set_position and pos:
            win32api.SetCursorPos(pos)
            sleep(round(uniform(0.04, 0.07), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        sleep(round(uniform(0.010, 0.025), 4))
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    def __get_random_outside_point(self):
        random_left = (self.window_rect[0], randint(self.window_rect[1], self.window_rect[3]))
        random_top = (randint(self.window_rect[0], self.window_rect[2]), self.window_rect[1])
        random_right = (self.window_rect[2], randint(self.window_rect[1], self.window_rect[3]))
        random_bottom = (randint(self.window_rect[0], self.window_rect[2]), self.window_rect[3])

        outside_points = (
            random_left,
            random_top,
            random_right,
            random_bottom,
        )
        return outside_points[randint(0, len(outside_points) - 1)]
