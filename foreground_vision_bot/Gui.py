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
        }
        sg.theme(theme)

    def init(self):
        layout = self.__get_layout()
        self.window = sg.Window("Flyff FVF", layout, location=(0, 0), resizable=True, finalize=True)
        sg.cprint_set_output_destination(self.window, "-ML-")
        self.__set_hotkeys()
        return self.window

    def loop(self, bot):
        while True:
            event, values = self.window.read(timeout=1000)

            # ACTIONS - Button events
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "-ATTACH_WINDOW-":
                game_window_name, game_window_handler = self.__attach_window_popup()
                if game_window_name and game_window_handler:
                    bot.stop()
                    bot.setup(game_window_handler, self.window)
                    truncated_game_window_name = (
                        game_window_name[:30] + "..." if len(game_window_name) > 30 else game_window_name
                    )
                    self.window["-ATTACHED_WINDOW-"].update(truncated_game_window_name)
                    self.window["-START_BOT-"].update(disabled=False)
                    self.window["-STOP_BOT-"].update(disabled=True)
                    self.window["-SELECT_MOBS-"].update(disabled=False)
            if event == "-START_BOT-":
                bot.start(self.window)
                self.window["-START_BOT-"].update(disabled=True)
                self.window["-STOP_BOT-"].update(disabled=False)
                self.window["-SELECT_MOBS-"].update(disabled=True)
            if event == "-STOP_BOT-":
                bot.stop()
                self.window["-START_BOT-"].update(disabled=False)
                self.window["-STOP_BOT-"].update(disabled=True)
                self.window["-SELECT_MOBS-"].update(disabled=False)

            # BOT OPTIONS - Video options
            if event == "-SHOW_FRAMES-":
                bot.set_config(show_frames=values["-SHOW_FRAMES-"])
                self.window["-SHOW_MATCHES_TEXT-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-SHOW_BOXES-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-SHOW_MARKERS-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-VISION_FRAME-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window.refresh()  # Combined with contents_changed, will compute the new size of the element
                self.window["-MAIN_COLUMN-"].contents_changed()
            if event == "-SHOW_BOXES-":
                bot.set_config(show_mobs_pos_boxes=values["-SHOW_BOXES-"])
            if event == "-SHOW_MARKERS-":
                bot.set_config(show_mobs_pos_markers=values["-SHOW_MARKERS-"])
            if event == "-SHOW_MATCHES_TEXT-":
                bot.set_config(show_matches_text=values["-SHOW_MATCHES_TEXT-"])

            # BOT OPTIONS - Threshold options
            if event.startswith("-BOT_THRESHOLD_OPTIONS-"):
                self.window["-BOT_THRESHOLD_OPTIONS-"].update(
                    visible=not self.window["-BOT_THRESHOLD_OPTIONS-"].visible
                )
                self.window["-BOT_THRESHOLD_OPTIONS-" + "-BUTTON-"].update(
                    self.window["-BOT_THRESHOLD_OPTIONS-"].metadata[0]
                    if self.window["-BOT_THRESHOLD_OPTIONS-"].visible
                    else self.window["-BOT_THRESHOLD_OPTIONS-"].metadata[1]
                )
                self.window.refresh()  # Combined with contents_changed, will compute the new size of the element
                self.window["-MAIN_COLUMN-"].contents_changed()
            if event == "-MOB_POS_MATCH_THRESHOLD-":
                bot.set_config(mob_pos_match_threshold=values["-MOB_POS_MATCH_THRESHOLD-"])
            if event == "-MOB_STILL_ALIVE_MATCH_THRESHOLD-":
                bot.set_config(mob_still_alive_match_threshold=values["-MOB_STILL_ALIVE_MATCH_THRESHOLD-"])
            if event == "-MOB_EXISTENCE_MATCH_THRESHOLD-":
                bot.set_config(mob_existence_match_threshold=values["-MOB_EXISTENCE_MATCH_THRESHOLD-"])
            if event == "-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-":
                bot.set_config(
                    inventory_perin_converter_match_threshold=values["-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-"]
                )
            if event == "-INVENTORY_ICONS_MATCH_THRESHOLD-":
                bot.set_config(inventory_icons_match_threshold=values["-INVENTORY_ICONS_MATCH_THRESHOLD-"])

            # BOT OPTIONS - General options
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
            if event == "-CONVERT_PENYA_TO_PERINS_TIMER_MIN-":
                try:
                    convert_penya_to_perins_timer_min = float(values["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"])
                    bot.set_config(convert_penya_to_perins_timer_min=convert_penya_to_perins_timer_min)
                except ValueError:
                    sg.cprint("Invalid convert penya to perins timer, must be in minutes")
                    self.window["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"].update("30")
                    bot.set_config(convert_penya_to_perins_timer_min=30)

            # STATUS - Text events
            if event in self.logger_events:
                sg.cprint(values[event], c=self.logger_events_color[event])
            if event == "video_fps":
                self.window["-VIDEO_FPS-"].update(values["video_fps"])

            # MOBS - Mobs configuration
            if event == "-SELECT_MOBS-":
                self.__select_mobs_popup()

            # VIDEO - Bot's Vision
            if values["-SHOW_FRAMES-"]:
                img = values.get("debug_frame", None)
                if img is not None:
                    resolution = values["-DEBUG_IMG_WIDTH-"]
                    w, h = self.frame_resolutions[resolution]
                    img = cv.resize(img, (w, h))
                    imgbytes = cv.imencode(".png", img)[1].tobytes()
                    self.window["-DEBUG_IMAGE-"].update(data=imgbytes)

    def close(self):
        self.window.close()

    def __set_hotkeys(self):
        self.window.bind("<Alt_L><s>", "-STOP_BOT-")

    def __get_layout(self):
        def Collapsible(layout, key, title="", collapsed=False):
            """
            User Defined Element
            A "collapsable section" element. Like a container element that can be collapsed and brought back
            :param layout:Tuple[List[sg.Element]]: The layout for the section
            :param key:Any: Key used to make this section visible / invisible
            :param title:str: Title to show next to arrow
            :param collapsed:bool: If True, then the section begins in a collapsed state
            :return:sg.Column: Column including the arrows, title and the layout that is pinned
            """
            arrows = (sg.SYMBOL_DOWN, sg.SYMBOL_UP)
            return sg.Column(
                [
                    [
                        sg.T((arrows[1] if collapsed else arrows[0]), enable_events=True, k=key + "-BUTTON-"),
                        sg.T(title, enable_events=True, key=key + "-TITLE-"),
                    ],
                    [sg.pin(sg.Column(layout, key=key, visible=not collapsed, metadata=arrows))],
                ],
                pad=(0, 0),
            )

        title = [sg.Text("Flyff FVF", font="Any 18")]

        actions = [
            sg.Frame(
                "Actions:",
                [
                    [
                        sg.Button("Attach Window", key="-ATTACH_WINDOW-"),
                        sg.Button("Start", disabled=True, key="-START_BOT-"),
                        sg.Button("Stop (Alt+s)", disabled=True, key="-STOP_BOT-"),
                        sg.Button("Exit"),
                    ],
                    [
                        sg.Text("Attached window: ", font="Any 8", pad=((5, 0), (0, 0))),
                        sg.Text("", font="Any 8", text_color="red", key="-ATTACHED_WINDOW-", pad=(0, 0)),
                    ],
                ],
                pad=((5, 15), (0, 5)),
                size=(290, 70),
            )
        ]
        mobs_config = [
            sg.Frame(
                "Mobs Configuration:",
                [
                    [
                        sg.Button("Select Mobs", key="-SELECT_MOBS-"),
                        sg.Button("Add Mob", disabled=True, key="-ADD_MOB-"),
                        sg.Button("Delete Mob", disabled=True, key="-DELETE_MOB-"),
                    ]
                ],
                pad=((5, 15), (10, 5)),
                size=(290, 55),
            )
        ]

        bot_threshold_options = [
            [sg.Text("Mob position Match Threshold:")],
            [
                sg.Slider(
                    (0.1, 0.9),
                    0.7,
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
                    0.7,
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
                    0.7,
                    0.05,
                    enable_events=True,
                    orientation="h",
                    size=(20, 15),
                    key="-MOB_EXISTENCE_MATCH_THRESHOLD-",
                ),
            ],
            [sg.Text("Inventory perin converter match threshold:")],
            [
                sg.Slider(
                    (0.1, 0.9),
                    0.7,
                    0.05,
                    enable_events=True,
                    orientation="h",
                    size=(20, 15),
                    key="-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-",
                ),
            ],
            [sg.Text("Inventory icons match threshold:")],
            [
                sg.Slider(
                    (0.1, 0.9),
                    0.7,
                    0.05,
                    enable_events=True,
                    orientation="h",
                    size=(20, 15),
                    key="-INVENTORY_ICONS_MATCH_THRESHOLD-",
                ),
            ],
        ]
        bot_options = [
            sg.Frame(
                "Options:",
                [
                    [sg.Checkbox("Show bot's vision", False, enable_events=True, key="-SHOW_FRAMES-")],
                    [
                        sg.pin(
                            sg.Checkbox(
                                "Show matches text",
                                False,
                                visible=False,
                                enable_events=True,
                                key="-SHOW_MATCHES_TEXT-",
                            )
                        )
                    ],
                    [
                        sg.pin(
                            sg.Checkbox("Show mobs boxes", False, visible=False, enable_events=True, key="-SHOW_BOXES-")
                        )
                    ],
                    [
                        sg.pin(
                            sg.Checkbox(
                                "Show mobs markers", False, visible=False, enable_events=True, key="-SHOW_MARKERS-"
                            )
                        )
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        Collapsible(
                            bot_threshold_options, "-BOT_THRESHOLD_OPTIONS-", "Threshold Options", collapsed=True
                        )
                    ],
                    [sg.HorizontalSeparator()],
                    [
                        sg.Text("Mobs kill goal:"),
                        sg.InputText("infinity", size=(10, 1), enable_events=True, key="-MOBS_KILL_GOAL-"),
                    ],
                    [
                        sg.Text("Fight Time Limit (s):"),
                        sg.InputText("8", size=(10, 1), enable_events=True, key="-FIGHT_TIME_LIMIT_SEC-"),
                    ],
                    [sg.Text("Delay to check if mob is still alive (s):")],
                    [
                        sg.InputText(
                            "0.25", size=(10, 1), enable_events=True, key="-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"
                        ),
                    ],
                    [sg.Text("Timer to convert penya to perins (m):")],
                    [
                        sg.InputText("30", size=(10, 1), enable_events=True, key="-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"),
                    ],
                ],
                pad=((5, 15), (5, 5)),
                expand_x=True,
            )
        ]
        bot_status = [
            sg.Frame(
                "Status:",
                [
                    [sg.Text("Video FPS:", size=(15, 1), key="-VIDEO_FPS-")],
                    [sg.Multiline(size=(35, 10), key="-ML-", autoscroll=True, expand_x=True)],
                ],
                pad=((5, 15), (5, 10)),
                expand_x=True,
            )
        ]
        main = sg.Column(
            [
                actions,
                mobs_config,
                bot_options,
                bot_status,
            ],
            pad=(0, 0),
            size=(300, 600),
            scrollable=True,
            vertical_scroll_only=True,
            expand_y=True,
            key="-MAIN_COLUMN-",
        )

        video = sg.Column(
            [
                [
                    sg.pin(
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
                            visible=False,
                            key="-VISION_FRAME-",
                        )
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
            size=(400, 100),
        )
        while True:
            event, values = popup_window.read()
            if event == "Refresh":
                handlers = get_window_handlers()
                popup_window["-DROP-"].update(values=list(handlers.keys()))
            if event in (sg.WIN_CLOSED, "Cancel"):
                popup_window.close()
                return None, None
            if event == "OK":
                popup_window.close()
                return values["-DROP-"], handlers[values["-DROP-"]]

    def __select_mobs_popup(self, all_mob=[], selected_mobs=[]):
        all_mobs = [
            {
                "name": "batto",
                "element": "wind",
                "location": "flaris",
            },
            {
                "name": "carvi",
                "element": "fire",
                "location": "flaris",
            },
            {
                "name": "castor",
                "element": "soil",
                "location": "darkon",
            },
            {
                "name": "ketiri",
                "element": "eletricity",
                "location": "darkon",
            },
            {
                "name": "kretan",
                "element": "eletricity",
                "location": "saint morning",
            },
        ]
        selected_mobs = [
            {
                "name": "batto",
                "element": "wind",
                "location": "flaris",
            },
            {
                "name": "ketiri",
                "element": "eletricity",
                "location": "darkon",
            },
        ]

        all_mobs_titles = [f"{mob['name']} - {mob['element']} - {mob['location']}" for mob in all_mobs]
        selected_mobs_titles = [f"{mob['name']} - {mob['element']} - {mob['location']}" for mob in selected_mobs]
        selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in selected_mobs_titles]

        popup_window = sg.Window(
            "Select Mobs",
            [
                [sg.Text("Please select the mobs to kill:")],
                [[sg.Text("Search: ")], [sg.Input(enable_events=True, expand_x=True, key="-MOBS_SEARCH-")]],
                [
                    sg.Listbox(
                        values=all_mobs_titles,
                        default_values=selected_mobs_titles,
                        size=(60, 10),
                        enable_events=True,
                        select_mode=sg.LISTBOX_SELECT_MODE_MULTIPLE,
                        key="-MOBS_LIST-",
                    )
                ],
                [sg.Button("Reset"), sg.OK()],
            ],
        )
        while True:
            event, values = popup_window.read()

            if event == sg.WIN_CLOSED:
                popup_window.close()
                return None

            if values["-MOBS_SEARCH-"] != "":
                search = values["-MOBS_SEARCH-"]
                filtered_mobs = [x for x in all_mobs_titles if search in x]
                popup_window["-MOBS_LIST-"].update(filtered_mobs)
            else:
                popup_window["-MOBS_LIST-"].update(all_mobs_titles)

            if event == "-MOBS_LIST-" and len(values["-MOBS_LIST-"]):
                selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in values["-MOBS_LIST-"]]
                popup_window["-MOBS_LIST-"].update(set_to_index=selected_mobs_indexes)

            if event == "OK":
                popup_window.close()
                return [all_mobs[i] for i in selected_mobs_indexes]
            if event == "Reset":
                popup_window["-MOBS_LIST-"].update(set_to_index=[])
