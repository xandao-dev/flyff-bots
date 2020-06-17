"""Foreground Vision Farm

Farm aproach: Using OpenCV it will track the name of the mob.
Currently I'm aiming to all lv 150 mobs in Neo Casdadia.
"""
from time import time, sleep

import cv2 as cv
import numpy as np
import pyttsx3
import win32con
import win32gui

from WindowCapture import WindowCapture
from human_mouse.HumanMouse import HumanMouse
from HumanKeyboard import HumanKeyboard, VKEY
from assets.Assets import MobNames, MobTypes, GeneralAssets
from helpers import start_countdown, print_logo, get_focused_window_handle

#Confs & Paths
debug = True
mob_height_offset = 125
time_check_mob_still_alive = 0.25
monster_kill_goal = 3
fight_time_limit = 8


def main(debug=False):
	voice_engine = pyttsx3.init()
	hwnd = get_focused_window_handle(voice_engine)
	window_capture = WindowCapture(hwnd)
	mouse = HumanMouse()
	keyboard = HumanKeyboard(hwnd)

	start_countdown(voice_engine, 3)

	mosters_killed = 0
	loop_time = time()
	while True:
		screenshot = window_capture.get_screenshot()
		screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)
		# Get the top of the screen
		top_image = screenshot[0:0+50, 200:screenshot.shape[1]-200]

		if not debug:
			points = get_mobs_position(
				MobNames.ROSPOSA, screenshot, mob_height_offset=mob_height_offset)
		else:
			points = get_mobs_position(
				MobNames.ROSPOSA, screenshot, mob_height_offset=mob_height_offset, debug_mode='points')
			#print(points)

			print('FPS {}'.format(round(1 / (time() - loop_time))))
			loop_time = time()
	
		if points:
			monsters_killed = mobs_available_on_screen(
				mouse, keyboard, window_capture, top_image, points, mosters_killed
			)
		else:
			mobs_not_available_on_screen(keyboard)

		if mosters_killed >= monster_kill_goal:
			break

		if cv.waitKey(1) == ord('q'):
			cv.destroyAllWindows()
			break


def get_mobs_position(needle_img, screenshot, mob_height_offset=80, threshold=0.6, debug_mode=None):
	# Save the dimensions of the needle image and the screenshot
	needle_w = needle_img.shape[1]
	needle_h = needle_img.shape[0]
	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Cut the skills bar on the bottom and the claim rewards button on the left side.
	screenshot_crop = screenshot[0:needle_h-55, 40:scrshot_w]

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result = cv.matchTemplate(screenshot_crop, needle_img, method)

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
				cv.rectangle(screenshot_crop, top_left, bottom_right, color=line_color,
							 lineType=line_type, thickness=2)
				img_resized = cv.resize(screenshot_crop, (975, 548))
				cv.imshow('Computer Vision', img_resized)
			elif debug_mode == 'points':
				# Draw the center point
				cv.drawMarker(screenshot_crop, (center_x, center_y),
							  color=marker_color, markerType=marker_type,
							  markerSize=40, thickness=2)
				# cv.putText(screenshot_crop, f'({center_x}, {center_y})', (x+w, y+h),
				#		   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
				img_resized = cv.resize(screenshot_crop, (975, 548))
				cv.imshow('Computer Vision', img_resized)

	return points


def mobs_available_on_screen(mouse, keyboard, window_capture, top_image, points, mosters_killed):
	mosters_count = mosters_killed
	mob_pos = points[round(len(points)/2)]
	mouse.move(to_point=mob_pos, duration=0.1)
	if check_mob_existence(GeneralAssets.MOB_LIFE_BAR, top_image):
		mouse.right_click(mob_pos)
		keyboard.press_key(win32con.VK_F1, press_time=0.06)
		fight_time = time()
		while True:
			if not check_mob_still_alive(MobTypes.WATER, window_capture):
				mosters_count += 1
				break
			else:
				if (time() - fight_time) >= fight_time_limit:
					break
				sleep(time_check_mob_still_alive)
	return mosters_count


def mobs_not_available_on_screen(keyboard):
	print('No Mobs in Area')
	keyboard.human_turn_back()
	keyboard.press_key(VKEY['w'], press_time=3)


def check_mob_existence(mob_life_bar, top_image, threshold=0.8, debug=False):
	if debug:
		cv.imshow("Mob Exists?", top_image)
		cv.waitKey(0)

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result = cv.matchTemplate(top_image, mob_life_bar, method)

	# Get the best match position from the match result.
	min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
	if max_val >= threshold:
		print('Mob found!')
		return True
	else:
		return False


def check_mob_still_alive(mob_type, window_capture, threshold=0.8, debug=False):
	# Take a new screenshot to verify the fight status
	screenshot = window_capture.get_screenshot()
	screenshot = cv.cvtColor(screenshot, cv.COLOR_BGR2GRAY)

	scrshot_w = screenshot.shape[1]
	scrshot_h = screenshot.shape[0]

	# Get the top of the screen to see if the mob life bar exists
	top_image = screenshot[0:0+50, 200:scrshot_w-200]

	if debug:
		cv.imshow("Mob Still Alive [Type Check]?", top_image)
		cv.waitKey(0)

	# There are 6 methods to choose from:
	# TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
	method = cv.TM_CCOEFF_NORMED
	result_type_check = cv.matchTemplate(top_image, mob_type, method)

	# Get the best match position from the match result.
	_, max_val_tc, _, _ = cv.minMaxLoc(result_type_check)

	if max_val_tc >= threshold:
		print('Mob still alive')
		return True
	else:
		print('No mob selected')
		return False


def self_buff(hwnd):
	pass


if __name__ == '__main__':
	print_logo('Flyff Farm Bot')
	main(debug)
