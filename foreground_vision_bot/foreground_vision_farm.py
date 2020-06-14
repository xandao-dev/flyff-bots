"""Foreground Vision Farm

Farm aproach: Using OpenCV it will track the name of the mob.
Currently I'm aiming to Batto(lv 150) in Neo Casdadia.
"""

from pathlib import Path
from time import time, sleep

import cv2 as cv
import keyboard
import numpy as np
import pyautogui
import win32api
import win32con
import win32gui
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string

from windowcapture import WindowCapture


def main(debug=False):
	hwnd = get_focused_window_handle()
	enemy_life_pixel = get_enemy_life_pixel()

	wincap = WindowCapture(hwnd)
	needle_img_path = str(Path(__file__).parent/'names'/'name.png')
	needle_img = cv.imread(needle_img_path, cv.IMREAD_GRAYSCALE)

	start_countdown(3)

	mosters_killed = 0
	loop_time = time()
	while(True):
		screenshot = wincap.get_screenshot()

		if debug:
			points, img = findClickPositions(
				needle_img, screenshot, mob_height_offset=120, debug_mode='points')
			print(points)
			img_resized = cv.resize(img, (975, 548))
			cv.imshow('Computer Vision', img_resized)

			print('FPS {}'.format(round(1 / (time() - loop_time))))
			loop_time = time()
		else:
			points, img = findClickPositions(
				needle_img, screenshot, mob_height_offset=120)

		if points:
			move_cursor(*points[0])
			if pyautogui.pixelMatchesColor(
					enemy_life_pixel[0],
					enemy_life_pixel[1],
					enemy_life_pixel[2],
					3):
				print('Mob found!')
				right_click(*points[0], True)
				keyboard.press('F1')
				mosters_killed += 1
				sleep(3)
		
		if mosters_killed > 5:
			break

		if cv.waitKey(1) == ord('q'):
			cv.destroyAllWindows()
			break


def findClickPositions(needle_img, screenshot, mob_height_offset=80, threshold=0.6, debug_mode=None):
	screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

	# Save the dimensions of the needle image
	needle_w = needle_img.shape[1]
	needle_h = needle_img.shape[0]

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result = cv.matchTemplate(screenshot, needle_img, method)

	# Get the all the positions from the match result that exceed our threshold
	locations = np.where(result >= threshold)
	locations = list(zip(*locations[::-1]))
	# print(locations)

	# You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
	# locations by using groupRectangles().
	# First we need to create the list of [x, y, w, h] rectangles
	rectangles = []
	for loc in locations:
		rect = [int(loc[0]), int(loc[1]), needle_w,
				needle_h + mob_height_offset]
		# Add every box to the list twice in order to retain single (non-overlapping) boxes
		rectangles.append(rect)
		rectangles.append(rect)
	# Apply group rectangles.
	# The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
	# done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
	# in the result. I've set eps to 0.5, which is:
	# "Relative difference between sides of the rectangles to merge them into a group."
	rectangles, weights = cv.groupRectangles(
		rectangles, groupThreshold=1, eps=0.5)
	# print(rectangles)

	points = []
	if len(rectangles):
		#print('Found needle.')

		line_color = (0, 255, 0)
		line_type = cv.LINE_4
		marker_color = (255, 0, 255)
		marker_type = cv.MARKER_CROSS

		# Loop over all the rectangles
		for (x, y, w, h) in rectangles:

			# Determine the center position
			center_x = x + int(w/2)
			center_y = y + int(h/2)
			# Save the points
			points.append((center_x, center_y))

			if debug_mode == 'rectangles':
				# Determine the box position
				top_left = (x, y)
				bottom_right = (x + w, y + h)
				# Draw the box
				cv.rectangle(screenshot, top_left, bottom_right, color=line_color,
							 lineType=line_type, thickness=2)
			elif debug_mode == 'points':
				# Draw the center point
				cv.drawMarker(screenshot, (center_x, center_y),
							  color=marker_color, markerType=marker_type,
							  markerSize=40, thickness=2)

	return points, screenshot


def get_enemy_life_pixel():
	"""Get enemy life(red bar) pixel position and color

	Returns:
					List: 0-> x, 1-> y, 2-> (rbg)
	"""
	print('\nClick inside the life enemy life to get the pixel color.')

	enemy_life_pixel = []

	def on_click(x, y, button, pressed):
		if pressed:
			enemy_life_pixel.extend((x, y, pyautogui.pixel(x, y)))
		if not pressed:
			return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	sleep(0.5)
	return enemy_life_pixel


def move_cursor(x, y):
	win32api.SetCursorPos((x, y))


def right_click(x, y, set_position=True):
	if set_position:
		win32api.SetCursorPos((x, y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def double_right_click(x, y, set_position=True):
	if set_position:
		win32api.SetCursorPos((x, y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def get_focused_window_handle():
	print('\nClick in the flyff window to get the process! The first click will be considered.')

	hwnd = []

	def on_click(x, y, button, pressed):
		if not pressed:
			hwnd.append(win32gui.GetForegroundWindow())
			return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	print('Window Selected: ', win32gui.GetWindowText(hwnd[0]))
	sleep(0.5)
	return hwnd[0]


# region Helpers
def start_countdown(sleep_time_sec=5):
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		sleep(sleep_time_sec/10)
	print('\nReady, forcing gnomes to work hard!')


def print_logo(text_logo: str):
	figlet = Figlet(font='slant')
	print(figlet.renderText(text_logo))
# endregion


if __name__ == '__main__':
	try:
		print_logo('Flyff Farm Bot')
		main()
	except Exception as e:
		print(str(e))
