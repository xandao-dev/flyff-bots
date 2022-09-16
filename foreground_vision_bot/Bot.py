from time import sleep, time
from threading import Thread

import cv2 as cv
import numpy as np
import pyttsx3

from assets.Assets import GeneralAssets, MobInfo
from utils.decorators import measure_perf
from utils.helpers import start_countdown, get_point_near_center
from utils.SyncedTimer import SyncedTimer
from libs.human_mouse.HumanMouse import HumanMouse
from libs.HumanKeyboard import VKEY, HumanKeyboard
from libs.WindowCapture import WindowCapture



class Bot:
    def __init__(self):
        self.config = {
            "show_frames": False,
            "show_mobs_pos_boxes": False,
            "show_mobs_pos_markers": False,
            "mob_pos_match_threshold": 0.7,
            "mob_still_alive_match_threshold": 0.7,
            "mob_existence_match_threshold": 0.7,
            "inventory_perin_converter_match_threshold": 0.7,
            "inventory_icons_match_threshold": 0.7,
            "mobs_kill_goal": None,
            "fight_time_limit_sec": 8,
            "delay_to_check_mob_still_alive_sec": 0.25,
            "convert_penya_to_perins_timer_min": 30,
        }

        # Debug Variables
        self.image_mobs_position = None

        # Synced Timers
        self.convert_penya_to_perins_timer = SyncedTimer(self.__convert_penya_to_perins, self.config["convert_penya_to_perins_timer_min"] * 60)

    def setup(self, window_handler):
        self.voice_engine = pyttsx3.init()
        self.window_capture = WindowCapture(window_handler)
        self.mouse = HumanMouse()
        self.keyboard = HumanKeyboard(window_handler)
        self.all_mobs = MobInfo.get_all_mobs()

    def start(self, gui_window):
        self.__farm_thread_running = True
        Thread(target=self.__farm_thread, args=(gui_window,), daemon=True).start()

    def stop(self):
        self.__farm_thread_running = False

    def set_config(self, **options):
        """Set the config options for the bot.

        :param \**options:
            show_frames: bool
                Show the video frames of the bot. Default: False
            show_mobs_pos_boxes: bool
                Show the boxes of the mobs positions. Default: False
            show_mobs_pos_markers: bool
                Show the markers of the mobs positions. Default: False
            mob_pos_match_threshold: float
                The threshold to match the mobs positions. From 0 to 1. Default: 0.7
            mob_still_alive_match_threshold: float
                The threshold to match if the mobs is still alive. From 0 to 1. Default: 0.7
            mob_existence_match_threshold: float
                The threshold to match the mob existence verification. From 0 to 1. Default: 0.7
            inventory_perin_converter_match_threshold: float
                The threshold to match the perin converter in the inventory. From 0 to 1. Default: 0.7
            inventory_icons_match_threshold: float
                The threshold to match if the inventory is open. From 0 to 1. Default: 0.7
            mobs_kill_goal: int
                The goal of mobs to kill, None for infinite. Default: None
            fight_time_limit_sec: int
                The time limit to fight the mob, after this time it will target another monster. Unity in seconds. Default: 8
            delay_to_check_mob_still_alive_sec: float
                The delay to check if the mob is still alive when it's fighting. Unity in seconds. Default: 0.25
            convert_penya_to_perins_timer_min: int
                The time to convert the penya to perins. Unity in minutes. Default: 30
        """
        for key, value in options.items():
            self.config[key] = value

        self.__update_timer_configs()

    def __update_timer_configs(self):
        self.convert_penya_to_perins_timer.wait_seconds = self.config["convert_penya_to_perins_timer_min"] * 60

    @measure_perf
    def __farm_thread(self, gui_window):
        start_countdown(self.voice_engine, 3)
        current_mob_info_index = 0
        mobs_killed = 0
        loop_time = time()

        while True:
            screenshot = self.window_capture.get_screenshot()

            self.convert_penya_to_perins_timer(GeneralAssets.INVENTORY_ICONS, GeneralAssets.INVENTORY_PERIN_CONVERTER)

            if current_mob_info_index >= (len(self.all_mobs) - 1):
                current_mob_info_index = 0
            mob_name_cv, mob_type_cv, mob_height_offset = self.all_mobs[current_mob_info_index]

            points = self.__get_mobs_position(mob_name_cv, screenshot, mob_height_offset)
            # print("Mobs positions: ", points)

            if points:
                mobs_killed = self.__mobs_available_on_screen(screenshot, mob_type_cv, points, mobs_killed)
            else:
                # TODO: Turn around and check for mobs first before changing the current mob
                current_mob_info_index += 1
                if current_mob_info_index >= (len(self.all_mobs) - 1):
                    self.__mobs_not_available_on_screen()
                else:
                    print("Current mob no found, checking another one.")

            if (self.config["mobs_kill_goal"] is not None) and (mobs_killed >= self.config["mobs_kill_goal"]):
                break

            if self.config["show_frames"]:
                gui_window.write_event_value("image_mobs_position", self.image_mobs_position)

            gui_window.write_event_value("msg_purple", f"Video FPS: {round(1 / (time() - loop_time))}")
            gui_window.write_event_value("msg_red", "Mobs killed: " + str(mobs_killed))
            loop_time = time()

            if not self.__farm_thread_running:
                break

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
        locations = np.where(result >= self.config["mob_pos_match_threshold"])
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

                if self.config["show_mobs_pos_boxes"]:
                    # Determine the box position
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    # Draw the box
                    cv.rectangle(screenshot, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
                if self.config["show_mobs_pos_markers"]:
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
                self.image_mobs_position = screenshot  # cv.resize(screenshot, (758, 426))

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

        if max_val_tc >= self.config["mob_still_alive_match_threshold"]:
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
        if max_val >= self.config["mob_existence_match_threshold"]:
            print(f"Mob found! Best mob_existence_match_threshold matched value: {max_val}")
            return True
        print(f"No mob found! Best mob_existence_match_threshold matched value: {max_val}")
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
        # self.mouse.move_like_robot(mob_pos_converted)
        if self.__check_mob_existence(GeneralAssets.MOB_LIFE_BAR, top_image):
            self.mouse.left_click(mob_pos)
            self.keyboard.hold_key(VKEY["F1"], press_time=0.06)
            self.mouse.move_outside_game()
            fight_time = time()
            while True:
                if not self.__check_mob_still_alive(mob_type_cv):
                    monsters_count += 1
                    break
                else:
                    if (time() - fight_time) >= self.config["fight_time_limit_sec"]:
                        # Unselect the mob if the fight limite is over
                        self.keyboard.hold_key(VKEY["esc"], press_time=0.06)
                        break
                    sleep(self.config["delay_to_check_mob_still_alive_sec"])
        return monsters_count

    def __mobs_not_available_on_screen(self):
        print("No Mobs in Area, moving.")
        self.keyboard.human_turn_back()
        self.keyboard.hold_key(VKEY["w"], press_time=4)

    def __check_if_inventory_is_open(self, frame, inventory_icons_cv):
        """
        Check if inventory is open looking if the icons of the inventory is available on the screen
        """
        needle_w = inventory_icons_cv.shape[0]
        needle_h = inventory_icons_cv.shape[1]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        method = cv.TM_CCOEFF_NORMED
        # Mask as the needle, to remove the black pixels
        result = cv.matchTemplate(frame, inventory_icons_cv, method)
        
        # Get the best match position from the match result.
        _, max_val, _, max_loc = cv.minMaxLoc(result)

        if max_val < self.config["inventory_icons_match_threshold"]:
            print(f"Inventory icons not found! Best inventory_icons_match_threshold matched value: {max_val}")
            return False
        print(f"Inventory icons found! Best inventory_icons_match_threshold matched value: {max_val}")

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        top_left = (max_loc[0], max_loc[1])
        bottom_right = (max_loc[0] + needle_w, max_loc[1] + needle_h)

        cv.rectangle(frame, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
        self.image_mobs_position = frame
        return True

    def __get_perin_converter_pos_if_available(self, frame, inventory_perin_converter_cv):
            needle_w = inventory_perin_converter_cv.shape[0]
            needle_h = inventory_perin_converter_cv.shape[1]

            # There are 6 methods to choose from:
            # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
            method = cv.TM_CCOEFF_NORMED
            result = cv.matchTemplate(frame, inventory_perin_converter_cv, method)

            # Get the best match position from the match result.
            _, max_val, _, max_loc = cv.minMaxLoc(result)

            if max_val < self.config["inventory_perin_converter_match_threshold"]:
                print(f"Inventory Perin Converter not found! Best inventory_perin_converter_match_threshold matched value: {max_val}")
                return None
            print(f"Inventory Perin Converter found! Best inventory_perin_converter_match_threshold matched value: {max_val}")
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            top_left = (max_loc[0], max_loc[1])
            bottom_right = (max_loc[0] + needle_w, max_loc[1] + needle_h)

            cv.rectangle(frame, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
            self.image_mobs_position = frame

            center_point = (round(max_loc[0] + needle_w / 2), round(max_loc[1] + needle_h / 2))
            return center_point
    
    def __convert_penya_to_perins(self, inventory_icons_cv, inventory_perin_converter_cv):
        # Open the inventory
        self.keyboard.press_key(VKEY["i"])
        sleep(1)
        frame = self.window_capture.get_screenshot()

        # Check if inventory is open
        is_inventory_open = self.__check_if_inventory_is_open(frame, inventory_icons_cv)
        if not is_inventory_open:
            # If not open, open it
            self.keyboard.press_key(VKEY["i"])
            sleep(1)
            frame = self.window_capture.get_screenshot()

            # Check if inventory is open, after one failed attempt
            is_inventory_open = self.__check_if_inventory_is_open(frame, inventory_icons_cv)
            if not is_inventory_open:
                return False

        # Check if perin converter is available
        center_point = self.__get_perin_converter_pos_if_available(frame, inventory_perin_converter_cv)
        if center_point is None:
            # If not available, close the inventory and return
            self.keyboard.press_key(VKEY["i"])
            return False
        
        # Move the mouse to the perin converter and click
        center_point_translated = self.window_capture.get_screen_position(center_point)
        self.mouse.move(to_point=center_point_translated, duration=0.2)
        self.mouse.left_click(center_point)
        sleep(0.5)

        # Press the convert button, based on a fixed offset from the perin converter
        convert_all_offset = (30, 40)
        convert_all_pos = (center_point[0] + convert_all_offset[0], center_point[1] + convert_all_offset[1])
        convert_all_pos_converted = self.window_capture.get_screen_position(convert_all_pos)
        self.mouse.move(to_point=convert_all_pos_converted, duration=0.2)
        self.mouse.left_click(convert_all_pos)
        sleep(0.5)

        # Close the inventory
        self.keyboard.press_key(VKEY["i"])
        return True