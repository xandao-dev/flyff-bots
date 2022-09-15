import PySimpleGUI as sg
import cv2 as cv

from utils.helpers import get_window_handlers


class Gui:
    def __init__(self, theme="DarkAmber"):
        self.logger_events = ["msg", "msg_red", "msg_purple", "msg_blue"]
        self.logger_events_color = {
            "msg": ("white", "black"),
            "msg_red": ("white", "red"),
            "msg_purple": ("white", "purple"),
            "msg_blue": ("white", "blue"),
        }
        self.frame_resolutions = {
            "160x120": (160, 120),
            "200x150": (200, 150),
            "320x240": (320, 240),
            "400x300": (400, 300),
            "640x480": (640, 480),
            "800x600": (800, 600),
            "1024x600": (1024, 600),
            "1024x768": (1024, 768),
            "1280x700": (1280, 700),
            "1280x720": (1280, 720),
            "1280x800": (1280, 800),
            "1280x1024": (1280, 1024),
            "1366x768": (1366, 768),
            "1400x1050": (1400, 1050),
            "1440x900": (1440, 900),
            "1600x900": (1600, 900),
            "1600x1200": (1600, 1200),
            "1680x1050": (1680, 1050),
            "1920x1000": (1920, 1000),
            "1920x1080": (1920, 1080),
        }
        sg.theme(theme)

    def init(self):
        layout = self.__get_layout()
        self.window = sg.Window("Flyff FVF", layout, location=(800, 400), resizable=True, finalize=True)
        sg.cprint_set_output_destination(self.window, "-ML-")
        return self.window

    def loop(self, bot):
        while True:
            event, values = self.window.read(timeout=1000)

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "-SHOW_FRAMES-":
                bot.set_config(show_frames=values["-SHOW_FRAMES-"])
                self.window["-SHOW_BOXES-"].update(disabled=(not values["-SHOW_FRAMES-"]))
                self.window["-SHOW_MARKERS-"].update(disabled=(not values["-SHOW_FRAMES-"]))
                if not values["-SHOW_FRAMES-"]:
                    self.window["-DEBUG_IMAGE-"].update(data=None)
            if event == "-SHOW_BOXES-":
                bot.set_config(show_mobs_pos_boxes=values["-SHOW_BOXES-"])
            if event == "-SHOW_MARKERS-":
                bot.set_config(show_mobs_pos_markers=values["-SHOW_MARKERS-"])
            if event == "-MOB_POS_MATCH_THRESHOLD-":
                bot.set_config(mob_pos_match_threshold=values["-MOB_POS_MATCH_THRESHOLD-"])
            if event == "-MOB_STILL_ALIVE_MATCH_THRESHOLD-":
                bot.set_config(mob_still_alive_match_threshold=values["-MOB_STILL_ALIVE_MATCH_THRESHOLD-"])
            if event == "-MOB_EXISTENCE_MATCH_THRESHOLD-":
                bot.set_config(mob_existence_match_threshold=values["-MOB_EXISTENCE_MATCH_THRESHOLD-"])
            if event == "-MOBS_KILL_GOAL-":
                if ["infinity", "inf", "0", ""] in values["-MOBS_KILL_GOAL-"].lower():
                    bot.set_config(mobs_kill_goal=None)
                else:
                    try:
                        mobs_kill_goal = int(values["-MOBS_KILL_GOAL-"])
                        bot.set_config(mobs_kill_goal=mobs_kill_goal)
                    except ValueError:
                        sg.cprint("Invalid mobs kill goal")
                        self.window["-MOBS_KILL_GOAL-"].update("infinity")
                        bot.set_config(mobs_kill_goal=None)
            if event == "-FIGHT_TIME_LIMIT_SEC-":
                try:
                    fight_time_limit_sec = int(values["-FIGHT_TIME_LIMIT_SEC-"])
                    bot.set_config(fight_time_limit_sec=fight_time_limit_sec)
                except ValueError:
                    sg.cprint("Invalid fight time limit")
                    self.window["-FIGHT_TIME_LIMIT_SEC-"].update("8")
                    bot.set_config(fight_time_limit_sec=8)
            if event == "-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-":
                try:
                    delay_to_check_mob_still_alive_sec = float(values["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"])
                    bot.set_config(delay_to_check_mob_still_alive_sec=delay_to_check_mob_still_alive_sec)
                except ValueError:
                    sg.cprint("Invalid delay to check if mob is still alive")
                    self.window["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"].update("0.25")
                    bot.set_config(delay_to_check_mob_still_alive_sec=0.25)

            if event in self.logger_events:
                sg.cprint(values[event], c=self.logger_events_color[event])

            if event == "-ATTACH_WINDOW-":
                window_handler = self.__attach_window_popup()
                if window_handler:
                    bot.stop()
                    bot.setup(window_handler)
                    self.window["-START_BOT-"].update(disabled=False)
                    self.window["-STOP_BOT-"].update(disabled=True)
            if event == "-START_BOT-":
                bot.start(self.window)
                self.window["-START_BOT-"].update(disabled=True)
                self.window["-STOP_BOT-"].update(disabled=False)
            if event == "-STOP_BOT-":
                bot.stop()
                self.window["-START_BOT-"].update(disabled=False)
                self.window["-STOP_BOT-"].update(disabled=True)

            if values["-SHOW_FRAMES-"]:
                img = values.get("image_mobs_position", None)
                if img is not None:
                    resolution = values["-DEBUG_IMG_WIDTH-"]
                    w, h = self.frame_resolutions[resolution]
                    img = cv.resize(img, (w, h))
                    imgbytes = cv.imencode(".png", img)[1].tobytes()
                    self.window["-DEBUG_IMAGE-"].update(data=imgbytes)

    def close(self):
        self.window.close()

    def __get_layout(self):
        title = [sg.Text("Flyff FVF", font="Any 18")]

        main = sg.Column(
            [
                [
                    sg.Frame(
                        "Actions:",
                        [
                            [
                                sg.Column(
                                    [
                                        [
                                            sg.Button("Attach Window", key="-ATTACH_WINDOW-"),
                                            sg.Button("Start", disabled=True, key="-START_BOT-"),
                                            sg.Button("Stop", disabled=True, key="-STOP_BOT-"),
                                            sg.Button("Exit"),
                                        ]
                                    ],
                                    pad=(0, 0),
                                )
                            ]
                        ],
                    )
                ],
                [
                    sg.Frame(
                        "Options:",
                        [
                            [sg.Checkbox("Show bot's vision", False, enable_events=True, key="-SHOW_FRAMES-")],
                            [sg.Checkbox("Show boxes", False, disabled=True, enable_events=True, key="-SHOW_BOXES-")],
                            [
                                sg.Checkbox(
                                    "Show markers", False, disabled=True, enable_events=True, key="-SHOW_MARKERS-"
                                )
                            ],
                            [sg.Text("Mob position Match Threshold:")],
                            [
                                sg.Slider(
                                    (0.1, 0.9),
                                    0.6,
                                    0.05,
                                    enable_events=True,
                                    orientation="h",
                                    size=(20, 15),
                                    key="-MOB_POS_MATCH_THRESHOLD-",
                                )
                            ],
                            [sg.Text("Mob still alive match threshold:")],
                            [
                                sg.Slider(
                                    (0.1, 0.9),
                                    0.6,
                                    0.05,
                                    enable_events=True,
                                    orientation="h",
                                    size=(20, 15),
                                    key="-MOB_STILL_ALIVE_MATCH_THRESHOLD-",
                                ),
                            ],
                            [sg.Text("Mob existence match threshold:")],
                            [
                                sg.Slider(
                                    (0.1, 0.9),
                                    0.6,
                                    0.05,
                                    enable_events=True,
                                    orientation="h",
                                    size=(20, 15),
                                    key="-MOB_EXISTENCE_MATCH_THRESHOLD-",
                                ),
                            ],
                            [
                                sg.Text("Mobs kill goal:"),
                                sg.InputText("infinity", size=(10, 1), key="-MOBS_KILL_GOAL-"),
                            ],
                            [
                                sg.Text("Fight Time Limit (s):"),
                                sg.InputText("8", size=(10, 1), key="-FIGHT_TIME_LIMIT_SEC-"),
                            ],
                            [sg.Text("Delay to check if mob is still alive (s):")],
                            [
                                sg.InputText("0.25", size=(10, 1), key="-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"),
                            ],
                        ],
                    )
                ],
                [
                    sg.Frame(
                        "Status:",
                        [
                            [sg.Text("", size=(15, 1), key="-OUTPUT-")],
                            [sg.Multiline(size=(30, 10), key="-ML-", autoscroll=True)],
                        ],
                    )
                ],
            ],
            pad=(0, 0),
            scrollable=True,
            vertical_scroll_only=True,
            expand_y=True,
        )

        video = sg.Column(
            [
                [
                    sg.Frame(
                        "Bot's Vision:",
                        [
                            [
                                sg.Text("Image Resolution:"),
                                sg.Combo(
                                    list(self.frame_resolutions.keys()),
                                    default_value="400x300",
                                    key="-DEBUG_IMG_WIDTH-",
                                ),
                            ],
                            [sg.Image(filename="", key="-DEBUG_IMAGE-")],
                        ],
                    )
                ]
            ],
            pad=(0, 0),
        )

        return [title, [main, video]]

    def __attach_window_popup(self):
        handlers = get_window_handlers()
        popup_window = sg.Window(
            "Attach Window",
            [
                [sg.Text("Please select the window to attach to:")],
                [sg.DropDown(list(handlers.keys()), key="-DROP-"), sg.Button("Refresh")],
                [sg.OK(), sg.Cancel()],
            ],
        )
        while True:
            event, values = popup_window.read()
            if event == "Refresh":
                handlers = get_window_handlers()
                popup_window["-DROP-"].update(values=list(handlers.keys()))
            if event in (sg.WIN_CLOSED, "Cancel"):
                popup_window.close()
                return None
            if event == "OK":
                popup_window.close()
                return handlers[values["-DROP-"]]
