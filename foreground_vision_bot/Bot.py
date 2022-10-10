from time import sleep, time
from threading import Thread
import collections
import pyttsx3

from assets.Assets import GeneralAssets, MobInfo
from utils.decorators import throttle
from utils.helpers import start_countdown, get_point_near_center
from utils.SyncedTimer import SyncedTimer
from libs.human_mouse.HumanMouse import HumanMouse
from libs.HumanKeyboard import VKEY, HumanKeyboard
from libs.WindowCapture import WindowCapture
from libs.ComputerVision import ComputerVision as CV


@throttle()
def emit_error(gui_window, msg):
    gui_window.write_event_value("msg_red", msg)


class Bot:
    def __init__(self):
        self.config = {
            "show_frames": False,
            "show_mobs_pos_boxes": False,
            "show_mobs_pos_markers": False,
            "show_matches_text": False,
            "mob_pos_match_threshold": 0.7,
            "mob_still_alive_match_threshold": 0.7,
            "mob_existence_match_threshold": 0.7,
            "inventory_perin_converter_match_threshold": 0.7,
            "inventory_icons_match_threshold": 0.7,
            "mobs_kill_goal": None,
            "fight_time_limit_sec": 8,
            "delay_to_check_mob_still_alive_sec": 0.25,
            "convert_penya_to_perins_timer_min": 30,
            "selected_mobs": [],
        }
        self.current_mob = None

        self.gui_window = None
        self.frame = None
        self.debug_frame = None
        self.__farm_thread_running = False

        # Synced Timers
        self.convert_penya_to_perins_timer = SyncedTimer(
            self.__convert_penya_to_perins, self.config["convert_penya_to_perins_timer_min"] * 60
        )

    def setup(self, window_handler, gui_window):
        self.gui_window = gui_window
        self.voice_engine = pyttsx3.init()
        self.wincap = WindowCapture(window_handler)
        self.mouse = HumanMouse(window_handler, self.wincap.get_screen_pos)
        self.keyboard = HumanKeyboard(window_handler)
        Thread(target=self.__frame_thread, daemon=True).start()
        gui_window.write_event_value("msg_green", "Bot is ready.")

    def start(self):
        self.__farm_thread_running = True
        Thread(target=self.__farm_thread, daemon=True).start()

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
            show_matches_text: bool
                Show text next to the matches. Default: False
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
            selected_mobs: list
                The list of mobs to kill. Default: []
        """
        for key, value in options.items():
            self.config[key] = value

        self.__update_timer_configs()

    def get_all_mobs(self):
        return MobInfo.get_all_mobs()

    def __update_timer_configs(self):
        self.convert_penya_to_perins_timer.wait_seconds = self.config["convert_penya_to_perins_timer_min"] * 60

    def __frame_thread(self):
        current_mob_info_index = 0
        fps_circular_buffer = collections.deque(maxlen=10)
        loop_time = time()
        while True:
            try:
                self.debug_frame, self.frame = self.wincap.get_frame()
            except:
                emit_error(
                    _throttle_sec=15,
                    gui_window=self.gui_window,
                    msg="Error getting the frame. Check if window is visible and attach again.",
                )
                sleep(3)
                continue

            if self.config["show_frames"]:
                if (len(self.config["selected_mobs"]) > 0):
                    if current_mob_info_index >= (len(self.config["selected_mobs"]) - 1):
                        current_mob_info_index = 0
                    self.current_mob = self.config["selected_mobs"][current_mob_info_index]
                    matches = self.__get_mobs_position(debug=True)
                    self.__check_mob_existence(debug=True)
                    self.__check_mob_still_alive(debug=True)
                    if not matches:
                        current_mob_info_index += 1
            
                self.__check_inventory_open(debug=True)
                self.__get_perin_converter_pos_if_available(debug=True)

            fps_circular_buffer.append(time() - loop_time)
            fps = round(1 / (sum(fps_circular_buffer) / len(fps_circular_buffer)))

            self.gui_window.write_event_value("debug_frame", self.debug_frame)
            self.gui_window.write_event_value("video_fps", f"Video FPS: {fps}")
            loop_time = time()

    def __farm_thread(self):
        start_countdown(self.voice_engine, 3)
        current_mob_info_index = 0
        mobs_killed = 0

        while True:
            if (len(self.config["selected_mobs"]) > 0):
                continue

            self.convert_penya_to_perins_timer()

            
            if current_mob_info_index >= (len(self.config["selected_mobs"]) - 1):
                current_mob_info_index = 0
            self.current_mob = self.config["selected_mobs"][current_mob_info_index]
            matches = self.__get_mobs_position()

            if matches:
                mobs_killed = self.__mobs_available_on_screen(matches, mobs_killed)
            else:
                # TODO: Turn around and check for mobs first before changing the current mob
                current_mob_info_index += 1
                if current_mob_info_index >= (len(self.config["selected_mobs"]) - 1):
                    self.__mobs_not_available_on_screen()
                else:
                    pass
                    # print("Current mob no found, checking another one.")

            if (self.config["mobs_kill_goal"] is not None) and (mobs_killed >= self.config["mobs_kill_goal"]):
                break

            if self.config["show_frames"]:
                self.gui_window.write_event_value("debug_frame", self.debug_frame)

            # self.gui_window.write_event_value("msg_red", "Mobs killed: " + str(mobs_killed))

            if not self.__farm_thread_running:
                break

    def __mobs_available_on_screen(self, points, mobs_killed):
        frame_w = self.frame.shape[1]
        frame_h = self.frame.shape[0]
        frame_center = (frame_w // 2, frame_h // 2)

        monsters_count = mobs_killed
        mob_pos = get_point_near_center(frame_center, points)
        self.mouse.move(to_point=mob_pos, duration=0.1)
        if self.__check_mob_existence():
            self.mouse.left_click()
            self.keyboard.hold_key(VKEY["F1"], press_time=0.06)
            self.mouse.move_outside_game(duration=0.2)
            fight_time = time()
            while True:
                if not self.__check_mob_still_alive():
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
        sleep(0.1)
        self.keyboard.press_key(VKEY["s"])

    def __convert_penya_to_perins(self):
        # Open the inventory
        self.keyboard.press_key(VKEY["i"])
        sleep(1)
        # Check if inventory is open
        is_inventory_open = self.__check_inventory_open()
        if not is_inventory_open:
            # If not open, open it
            self.keyboard.press_key(VKEY["i"])
            sleep(1)

            # Check if inventory is open, after one failed attempt
            is_inventory_open = self.__check_inventory_open()
            if not is_inventory_open:
                return False

        # Check if perin converter is available
        center_point = self.__get_perin_converter_pos_if_available()
        if center_point is None:
            # If not available, close the inventory and return
            self.keyboard.press_key(VKEY["i"])
            return False

        # Move the mouse to the perin converter and click
        self.mouse.move(to_point=center_point, duration=0.2)
        self.mouse.left_click()
        sleep(0.5)

        # Press the convert button, based on a fixed offset from the perin converter
        convert_all_offset = (30, 40)
        convert_all_pos = (center_point[0] + convert_all_offset[0], center_point[1] + convert_all_offset[1])
        self.mouse.move(to_point=convert_all_pos, duration=0.2)
        self.mouse.left_click()
        sleep(0.5)

        # Close the inventory
        self.keyboard.press_key(VKEY["i"])
        return True

    """Match Methods"""

    def __get_mobs_position(self, debug=False):
        if self.current_mob["image"] is None or self.current_mob["height_offset"] is None:
            return []

        # frame_cute_area 50px from each side of the frame to avoid some UI elements
        matches, drawn_frame = CV.match_template_multi(
            frame=self.frame,
            crop_area=(50, -50, 50, -50),
            template=self.current_mob["image"],
            threshold=self.config["mob_pos_match_threshold"],
            box_offset=(0, self.current_mob["height_offset"]),
            frame_to_draw=self.debug_frame if debug else None,
            draw_rect=self.config["show_mobs_pos_boxes"],
            draw_marker=self.config["show_mobs_pos_markers"],
            draw_text=self.config["show_matches_text"],
        )
        if debug:
            self.debug_frame = drawn_frame

        # print("Mobs positions: ", matches)
        return matches

    def __check_mob_still_alive(self, debug=False):
        """
        Check if the mob is still alive by checking if the mob type icon is still visible.
        We can't use mob life bar because it changes when the mob is hit.
        """
        # frame_cute_area get the top of the screen to see if the mob type icon is still visible
        _, _, _, passed_threshold, drawn_frame = CV.match_template(
            frame=self.frame,
            crop_area=(0, 50, 200, -200),
            template=self.current_mob["element"],
            threshold=self.config["mob_still_alive_match_threshold"],
            frame_to_draw=self.debug_frame if debug else None,
            text_to_draw="Mob still alive" if debug and self.config["show_matches_text"] else None,
        )
        if debug:
            self.debug_frame = drawn_frame

        if passed_threshold:
            # print(f"Mob still alive. mob_still_alive_match_threshold: {max_val}")
            return True
        # print(f"No mob selected. mob_still_alive_match_threshold: {max_val}")
        return False

    def __check_mob_existence(self, debug=False):
        """
        Check if the mob exists by checking if the mob life bar exists.
        It's better to use mob life bar than mob type icon because mob life bar is bigger,
        so it's faster to match.
        """

        # frame_cute_area get the top of the screen to see if the mob life bar exists
        _, _, _, passed_threshold, drawn_frame = CV.match_template(
            frame=self.frame,
            crop_area=(0, 50, 200, -200),
            template=GeneralAssets.MOB_LIFE_BAR,
            threshold=self.config["mob_existence_match_threshold"],
            frame_to_draw=self.debug_frame if debug else None,
            text_to_draw="Mob exists" if debug and self.config["show_matches_text"] else None,
        )
        if debug:
            self.debug_frame = drawn_frame

        if passed_threshold:
            # print(f"Mob found! mob_existence_match_threshold: {max_val}")
            return True
        # print(f"No mob found! mob_existence_match_threshold: {max_val}")
        return False

    def __check_inventory_open(self, debug=False):
        """
        Check if inventory is open looking if the icons of the inventory is available on the screen.
        """
        _, _, _, passed_threshold, drawn_frame = CV.match_template(
            frame=self.frame,
            template=GeneralAssets.INVENTORY_ICONS,
            threshold=self.config["inventory_icons_match_threshold"],
            frame_to_draw=self.debug_frame if debug else None,
            text_to_draw="Inv. open" if debug and self.config["show_matches_text"] else None,
        )
        if debug:
            self.debug_frame = drawn_frame

        if passed_threshold:
            # print(f"Inventory is open! inventory_icons_match_threshold: {max_val}")
            return True
        # print(f"Inventory is closed! inventory_icons_match_threshold: {max_val}")
        return False

    def __get_perin_converter_pos_if_available(self, debug=False):
        """
        Get position of perin converter button in inventory, if available, otherwise return None
        """

        # frame_cute_area 300px from top, because the inventory is big
        _, _, center_loc, passed_threshold, drawn_frame = CV.match_template(
            frame=self.frame,
            crop_area=(300, 0, 0, 0),
            template=GeneralAssets.INVENTORY_PERIN_CONVERTER,
            threshold=self.config["inventory_perin_converter_match_threshold"],
            frame_to_draw=self.debug_frame if debug else None,
            text_to_draw="P. converter" if debug and self.config["show_matches_text"] else None,
        )
        if debug:
            self.debug_frame = drawn_frame

        if passed_threshold:
            # print(f"Perin converter found! inventory_perin_converter_match_threshold: {max_val}")
            return center_loc
        # print(f"Perin converter not found! inventory_perin_converter_match_threshold: {max_val}")
