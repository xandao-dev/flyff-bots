"""Foreground Vision Farm

Farm aproach: Using OpenCV it will track the name of the mob.
Currently I'm aiming to Batto(lv 150) in Neo Casdadia.
"""

from pathlib import Path
from time import time, sleep

import cv2 as cv
import numpy as np
import pyautogui
import pyttsx3
import win32api
import win32con
import win32gui
from random import randint, choice
from math import ceil
from ctypes import windll
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string

from WindowCapture import WindowCapture
from human_mouse.HumanMouse import HumanMouse

#Confs & Paths
debug = False
mob_height_offset = 120
sleep_time_to_check_enemy_existence = 0.5
monster_kill_goal = 7

mob_name_path = str(Path(__file__).parent/'assets'/'names'/'batto.png')
mob_full_life_path = str(Path(__file__).parent/'assets'/'mob_full_life.png')
mob_type_path = str(Path(__file__).parent / 'assets'/'mob_type_wind.png')


def main(debug=False):
	voice_engine = pyttsx3.init()
	hwnd = get_focused_window_handle(voice_engine)
	window_capture = WindowCapture(hwnd)
	human_mouse = HumanMouse()

	needle_img = cv.imread(mob_name_path, cv.IMREAD_GRAYSCALE)
	mob_full_life = cv.imread(mob_full_life_path, cv.IMREAD_GRAYSCALE)
	mob_type = cv.imread(mob_type_path, cv.IMREAD_GRAYSCALE)

	start_countdown(voice_engine, 3)

	mosters_killed = 0
	loop_time = time()
	while(True):
		screenshot = window_capture.get_screenshot()
		screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
		# Get the top of the screen
		top_image = screenshot[0:0+50, 200:screenshot.shape[1]-200]

		if not debug:
			points = get_mobs_position(
				needle_img, screenshot, mob_height_offset=mob_height_offset)
		else:
			points = get_mobs_position(
				needle_img, screenshot, mob_height_offset=mob_height_offset, debug_mode='points')
			print(points)

			print('FPS {}'.format(round(1 / (time() - loop_time))))
			loop_time = time()

		if points:
			mob_pos = points[round(len(points)/2)]
			human_mouse.move(mob_pos, 0.1)
			if check_mob_existence(mob_full_life, top_image):
				human_mouse.right_click(mob_pos)
				press_key(hwnd, win32con.VK_F1)
				human_mouse.move_random_corner(0.1)
				while True:
					if not check_mob_still_alive(mob_type, window_capture):
						mosters_killed += 1
						break
					else:
						sleep(0.5)

		if mosters_killed >= monster_kill_goal:
			break

		if cv.waitKey(1) == ord('q'):
			cv.destroyAllWindows()
			break


def get_focused_window_handle(voice_engine):
	print('\nClick in the flyff window to get the process! The first click will be considered.')
	voice_engine.say('Selecione a tela do jogo')

	hwnd = []

	def on_click(x, y, button, pressed):
		if not pressed:
			hwnd.append(win32gui.GetForegroundWindow())
			return False

	voice_engine.runAndWait()
	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	print('Window Selected: ', win32gui.GetWindowText(hwnd[0]))
	sleep(0.5)
	return hwnd[0]


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


def get_mobs_position(needle_img, screenshot, mob_height_offset=80, threshold=0.6, debug_mode=None):
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
				img_resized = cv.resize(screenshot, (975, 548))
				cv.imshow('Computer Vision', img_resized)
			elif debug_mode == 'points':
				# Draw the center point
				cv.drawMarker(screenshot, (center_x, center_y),
							  color=marker_color, markerType=marker_type,
							  markerSize=40, thickness=2)
				# cv.putText(screenshot, f'({center_x}, {center_y})', (x+w, y+h),
				#		   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
				img_resized = cv.resize(screenshot, (975, 548))
				cv.imshow('Computer Vision', img_resized)

	return points


def check_mob_existence(mob_full_life, top_image, threshold=0.8, debug=False):
	if debug:
		cv.imshow("Mob Exists?", top_image)
		cv.waitKey(0)

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result = cv.matchTemplate(top_image, mob_full_life, method)

	# Get the best match position from the match result.
	min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
	if max_val >= threshold:
		print('Mob found!')
		return True
	else:
		return False


def atack_mob():
	pass


#Check if the mob type icon is visible
def check_mob_still_alive(mob_type, window_capture, threshold=0.8, debug=False):
	# Take a new screenshot to verify the fight status
	screenshot = window_capture.get_screenshot()
	screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
	# Get the top of the screen to see if the mob life bar exists
	top_image = screenshot[0:0+50, 200:screenshot.shape[1]-200]

	if debug:
		cv.imshow("Mob Still Alive?", top_image)
		cv.waitKey(0)

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result = cv.matchTemplate(top_image, mob_type, method)

	# Get the best match position from the match result.
	min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
	if max_val >= threshold:
		print('Mob still alive')
		return True
	else:
		print('No mob selected')
		return False


def search_new_mobs():
	pass


# region Helpers
def start_countdown(voice_engine, sleep_time_sec=5):
	voice_engine.say(f'Iniciando em {sleep_time_sec} segundos')
	voice_engine.runAndWait()
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		sleep(sleep_time_sec/10)
	print('\nReady, forcing dwarves to work!')


def print_logo(text_logo: str):
	figlet = Figlet(font='slant')
	print(figlet.renderText(text_logo))


# Keys: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
def press_key(hwnd, key, press_time=0.2):
	# 1/0.015-> Time average for each iteration
	for i in range(round(press_time*(1/0.015))):
		win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
		sleep(0.005)
		win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0)
		sleep(0.01)
# endregion


if __name__ == '__main__':
	print_logo('Flyff Farm Bot')
	main(debug)