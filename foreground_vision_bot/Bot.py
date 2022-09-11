from time import sleep, time

import cv2 as cv
import numpy as np
import pyttsx3
import win32con

from assets.Assets import GeneralAssets, MobInfo
from utils.helpers import get_focused_window_handle, start_countdown, get_point_near_center
from libs.human_mouse.HumanMouse import HumanMouse
from libs.HumanKeyboard import VKEY, HumanKeyboard
from libs.WindowCapture import WindowCapture

# Configs & Paths
debug = True
time_check_mob_still_alive = 0.25
mobs_kill_goal = 99999
fight_time_limit = 8


class Bot:
    def __init__(self):
        # Debug Options
        self.debug_show_mobs_pos_boxes = True
        self.debug_show_mobs_pos_points = False

        # Debug Variables
        self.debug_image_mobs_pos_boxes = None
        self.debug_image_mobs_pos_points = None

        # Options
        self.get_mobs_position_threshold = 0.6
        self.check_mob_still_alive_threshold = 0.6
        self.check_mob_existence_threshold = 0.5

        # Instances
        self.voice_engine = pyttsx3.init()
        self.hwnd = get_focused_window_handle(self.voice_engine)
        self.window_capture = WindowCapture(self.hwnd)
        self.mouse = HumanMouse()
        self.keyboard = HumanKeyboard(self.hwnd)
        self.all_mobs = MobInfo.get_all_mobs()

        start_countdown(self.voice_engine, 3)

    def __get_mobs_position(self, mob_name_cv, screenshot, mob_height_offset):
        # Save the dimensions of the needle image and the screenshot
        needle_w = mob_name_cv.shape[1]
        needle_h = mob_name_cv.shape[0]
        scrshot_w = screenshot.shape[1]
        scrshot_h = screenshot.shape[0]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        method = cv.TM_CCOEFF_NORMED
        result = cv.matchTemplate(screenshot, mob_name_cv, method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= self.get_mobs_position_threshold)
        locations = list(zip(*locations[::-1]))
        # print(locations)

        # You'll notice a lot of overlapping rectangles get drawn. We can eliminate those redundant
        # locations by using groupRectangles().
        # First we need to create the list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), needle_w, needle_h + mob_height_offset]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)
        # Apply group rectangles.
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is
        # done. If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # in the result. I've set eps to 0.5, which is:
        # "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        # print(rectangles)

        points = []
        if len(rectangles):
            # print('Found needle.')
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            marker_color = (255, 0, 255)
            marker_type = cv.MARKER_CROSS

            # Loop over all the rectangles
            for (x, y, w, h) in rectangles:
                # Determine the center position
                center_x = x + int(w / 2)
                center_y = y + int(h / 2)
                # Save the points
                points.append((center_x, center_y))

                if self.debug_show_mobs_pos_boxes:
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(screenshot, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
                    self.debug_image_mobs_pos_boxes = cv.resize(screenshot, (975, 548))
                if self.debug_show_mobs_pos_points:
                    # Draw the center point
                    cv.drawMarker(
                        screenshot,
                        (center_x, center_y),
                        color=marker_color,
                        markerType=marker_type,
                        markerSize=40,
                        thickness=2,
                    )
                    # cv.putText(screenshot, f'({center_x}, {center_y})', (x+w, y+h),
                    # 		   cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
                    self.debug_image_mobs_pos_points = cv.resize(screenshot, (758, 426))

        # Remove points in the skills bar on the bottom and the claim rewards button on the left side.
        for point in points:
            if point[0] <= 40 or point[1] >= needle_h - 55:
                points.remove(point)

        return points

    def __check_mob_still_alive(self, mob_type_cv, debug=False):
        # Take a new screenshot to verify the fight status
        screenshot = self.window_capture.get_screenshot()

        scrshot_w = screenshot.shape[1]
        scrshot_h = screenshot.shape[0]

        # Get the top of the screen to see if the mob life bar exists
        top_image = screenshot[0 : 0 + 50, 200 : scrshot_w - 200]

        if debug:
            cv.imshow("Mob Still Alive [Type Check]?", top_image)
            cv.waitKey(0)

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        method = cv.TM_CCOEFF_NORMED
        result_type_check = cv.matchTemplate(top_image, mob_type_cv, method)

        # Get the best match position from the match result.
        _, max_val_tc, _, _ = cv.minMaxLoc(result_type_check)

        if max_val_tc >= self.check_mob_still_alive_threshold:
            print("Mob still alive")
            return True
        else:
            print("No mob selected")
            return False

    def __check_mob_existence(self, mob_life_bar, top_image, debug=False):
        if debug:
            cv.imshow("Mob Exists?", top_image)
            cv.waitKey(0)

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        method = cv.TM_CCOEFF_NORMED
        result = cv.matchTemplate(top_image, mob_life_bar, method)

        # Get the best match position from the match result.
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)
        if max_val >= self.check_mob_existence_threshold:
            print(f"Mob found! Best check_mob_existence_threshold matched value: {max_val}")
            return True
        print(f"No mob found! Best check_mob_existence_threshold matched value: {max_val}")
        return False

    def __mobs_available_on_screen(self, screenshot, mob_type_cv, points, mobs_killed):
        scrshot_w = screenshot.shape[1]
        scrshot_h = screenshot.shape[0]
        scrshot_center = (round(scrshot_w / 2), round(scrshot_h / 2))

        # Get the top of the screen
        top_image = screenshot[0 : 0 + 50, 200 : scrshot_w - 200]

        monsters_count = mobs_killed
        mob_pos = get_point_near_center(scrshot_center, points)
        mob_pos_converted = self.window_capture.get_screen_position(mob_pos)
        self.mouse.move(to_point=mob_pos_converted, duration=0.1)
        #self.mouse.move_like_robot(mob_pos_converted)
        if self.__check_mob_existence(GeneralAssets.MOB_LIFE_BAR, top_image):
            self.mouse.right_click(mob_pos)
            self.keyboard.press_key(win32con.VK_F1, press_time=0.06)
            fight_time = time()
            fight_time_limit_count = 0
            while True:
                if not self.__check_mob_still_alive(mob_type_cv):
                    monsters_count += 1
                    break
                else:
                    if (time() - fight_time) >= fight_time_limit:
                        # Unselect the mob if the fight limite is over
                        self.keyboard.press_key(win32con.VK_ESCAPE, press_time=0.06)
                        break
                    sleep(time_check_mob_still_alive)
        return monsters_count

    def __mobs_not_available_on_screen(self):
        print("No Mobs in Area, moving.")
        self.keyboard.human_turn_back()
        self.keyboard.press_key(VKEY["w"], press_time=4)

    def farm_thread(self):
        current_mob_info_index = 0
        mobs_killed = 0
        loop_time = time()

        while True:
            screenshot = self.window_capture.get_screenshot()

            if current_mob_info_index >= (len(self.all_mobs) - 1):
                current_mob_info_index = 0
            mob_name_cv, mob_type_cv, mob_height_offset = self.all_mobs[current_mob_info_index]

            points = self.__get_mobs_position(mob_name_cv, screenshot, mob_height_offset)
            #print("Mobs positions: ", points)

            #print("FPS {}".format(round(1 / (time() - loop_time))))
            loop_time = time()

            if points:
                mobs_killed = self.__mobs_available_on_screen(screenshot, mob_type_cv, points, mobs_killed)
            else:
                # TODO: Turn around and check for mobs first before changing the current mob
                current_mob_info_index += 1
                if current_mob_info_index >= (len(self.all_mobs) - 1):
                    self.__mobs_not_available_on_screen()
                else:
                    print("Current mob no found, checking another one.")

            if mobs_killed >= mobs_kill_goal:
                break

            if cv.waitKey(1) == ord("q"):
                cv.destroyAllWindows()
                break
