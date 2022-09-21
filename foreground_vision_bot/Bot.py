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
from libs.ComputerVision import ComputerVision as CV


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
        self.convert_penya_to_perins_timer = SyncedTimer(
            self.__convert_penya_to_perins, self.config["convert_penya_to_perins_timer_min"] * 60
        )

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
            frame = self.window_capture.get_screenshot()

            self.convert_penya_to_perins_timer(GeneralAssets.INVENTORY_ICONS, GeneralAssets.INVENTORY_PERIN_CONVERTER)

            if current_mob_info_index >= (len(self.all_mobs) - 1):
                current_mob_info_index = 0
            mob_name_cv, mob_type_cv, mob_height_offset = self.all_mobs[current_mob_info_index]

            matches = self.__get_mobs_position(mob_name_cv, frame, mob_height_offset)
            # print("Mobs positions: ", matches)

            if matches:
                mobs_killed = self.__mobs_available_on_screen(frame, mob_type_cv, matches, mobs_killed)
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

    def __get_mobs_position(self, mob_name_cv, frame, mob_height_offset):
        # Cut 50px from each side of the frame to avoid some UI elements
        frame = frame[50:-50, 50:-50]
        matches, frame = CV.match_template_multi(
            frame=frame,
            template=mob_name_cv,
            threshold=self.config["mob_pos_match_threshold"],
            box_offset=(0, mob_height_offset),
            draw_rect=self.config["show_mobs_pos_boxes"],
            draw_marker=self.config["show_mobs_pos_markers"],
        )
        # Add 50px to the x and y positions to compensate the cut
        matches = [(x + 50, y + 50) for x, y in matches]

        self.image_mobs_position = frame
        return matches

    def __check_mob_still_alive(self, mob_type_cv):
        """
        Check if the mob is still alive by checking if the mob type icon is still visible.
        """
        frame = self.window_capture.get_screenshot()
        frame_w = frame.shape[1]

        # Get the top of the screen to see if the mob life bar exists
        top_image = frame[0 : 0 + 50, 200 : frame_w - 200]

        max_val, _, _, pass_threshold, frame = CV.match_template(
            frame=top_image, template=mob_type_cv, threshold=self.config["mob_still_alive_match_threshold"]
        )
        self.image_mob_still_alive = frame

        if pass_threshold:
            print(f"Mob still alive. mob_still_alive_match_threshold: {max_val}")
            return True
        else:
            print(f"No mob selected. mob_still_alive_match_threshold: {max_val}")
            return False

    def __check_mob_existence(self, mob_life_bar, top_image):
        """
        Check if the mob exists by checking if the mob life bar exists.
        """

        max_val, _, _, pass_threshold, frame = CV.match_template(
            frame=top_image, template=mob_life_bar, threshold=self.config["mob_existence_match_threshold"]
        )
        # self.image_mobs_position = frame

        if pass_threshold:
            print(f"Mob found! mob_existence_match_threshold: {max_val}")
            return True
        else:
            print(f"No mob found! mob_existence_match_threshold: {max_val}")
            return False

    def __mobs_available_on_screen(self, frame, mob_type_cv, points, mobs_killed):
        frame_w = frame.shape[1]
        frame_h = frame.shape[0]
        frame_center = (frame_w // 2, frame_h // 2)

        # Get the top of the screen
        top_image = frame[0 : 0 + 50, 200 : frame_w - 200]

        monsters_count = mobs_killed
        mob_pos = get_point_near_center(frame_center, points)
        mob_pos_converted = self.window_capture.get_screen_position(mob_pos)
        self.mouse.move(to_point=mob_pos_converted, duration=0.1)
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
        time.sleep(0.1)
        self.keyboard.press_key(VKEY["s"])


    def __check_if_inventory_is_open(self, frame, inventory_icons_cv):
        """
        Check if inventory is open looking if the icons of the inventory is available on the screen
        """
        max_val, _, _, pass_threshold, frame = self.__check_if_inventory_is_open_cv(
            frame=frame, template=inventory_icons_cv, threshold=self.config["inventory_icons_match_threshold"]
        )
        # self.image_mobs_position = frame
        if pass_threshold:
            print(f"Inventory is open! inventory_icons_match_threshold: {max_val}")
            return True
        print(f"Inventory is closed! inventory_icons_match_threshold: {max_val}")
        return False

    def __get_perin_converter_pos_if_available(self, frame, inventory_perin_converter_cv):
        """
        Get position of perin converter button in inventory, if available, otherwise return None
        """
        max_val, _, center_loc, pass_threshold, frame = CV.match_template(
            frame=frame,
            template=inventory_perin_converter_cv,
            threshold=self.config["inventory_perin_converter_match_threshold"],
        )
        # self.image_mobs_position = frame

        if pass_threshold:
            print(f"Perin converter found! inventory_perin_converter_match_threshold: {max_val}")
            return center_loc
        print(f"Perin converter not found! inventory_perin_converter_match_threshold: {max_val}")

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
