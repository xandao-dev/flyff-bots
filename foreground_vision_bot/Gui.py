import difflib

import cv2 as cv
import PySimpleGUI as sg
from utils.helpers import get_window_handlers, hex_variant

import re


class Gui:
    def __init__(self, theme="DarkAmber"):
        self.logger_events = ["msg", "msg_red", "msg_purple", "msg_blue", "msg_green"]
        self.logger_events_color = {
            "msg": ("white", "black"),
            "msg_red": ("white", "red"),
            "msg_purple": ("white", "purple"),
            "msg_blue": ("white", "blue"),
            "msg_green": ("white", "green"),
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
        sg.user_settings_filename(path=".")
        self.__set_hotkeys()
        return self.window

    def loop(self, bot):
        self.__load_settings(bot)
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
            if event == "-START_BOT-":
                bot.start()
                self.window["-START_BOT-"].update(disabled=True)
                self.window["-STOP_BOT-"].update(disabled=False)
            if event == "-STOP_BOT-":
                bot.stop()
                self.window["-START_BOT-"].update(disabled=False)
                self.window["-STOP_BOT-"].update(disabled=True)

            # BOT OPTIONS - Video options
            if event == "-SHOW_FRAMES-":
                bot.set_config(show_frames=values["-SHOW_FRAMES-"])
                self.window["-SHOW_MATCHES_TEXT-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-SHOW_BOXES-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-SHOW_MARKERS-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window["-VISION_FRAME-"].update(visible=(values["-SHOW_FRAMES-"]))
                self.window.refresh()  # Combined with contents_changed, will compute the new size of the element
                self.window["-MAIN_COLUMN-"].contents_changed()
            if event == "-SHOW_MATCHES_TEXT-":
                bot.set_config(show_matches_text=values["-SHOW_MATCHES_TEXT-"])
                sg.user_settings_set_entry("-SHOW_MATCHES_TEXT-", values["-SHOW_MATCHES_TEXT-"])
            if event == "-SHOW_BOXES-":
                bot.set_config(show_mobs_pos_boxes=values["-SHOW_BOXES-"])
                sg.user_settings_set_entry("-SHOW_BOXES-", values["-SHOW_BOXES-"])
            if event == "-SHOW_MARKERS-":
                bot.set_config(show_mobs_pos_markers=values["-SHOW_MARKERS-"])
                sg.user_settings_set_entry("-SHOW_MARKERS-", values["-SHOW_MARKERS-"])

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
                sg.user_settings_set_entry("-MOB_POS_MATCH_THRESHOLD-", values["-MOB_POS_MATCH_THRESHOLD-"])
            if event == "-MOB_STILL_ALIVE_MATCH_THRESHOLD-":
                bot.set_config(mob_still_alive_match_threshold=values["-MOB_STILL_ALIVE_MATCH_THRESHOLD-"])
                sg.user_settings_set_entry(
                    "-MOB_STILL_ALIVE_MATCH_THRESHOLD-", values["-MOB_STILL_ALIVE_MATCH_THRESHOLD-"]
                )
            if event == "-MOB_EXISTENCE_MATCH_THRESHOLD-":
                bot.set_config(mob_existence_match_threshold=values["-MOB_EXISTENCE_MATCH_THRESHOLD-"])
                sg.user_settings_set_entry("-MOB_EXISTENCE_MATCH_THRESHOLD-", values["-MOB_EXISTENCE_MATCH_THRESHOLD-"])
            if event == "-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-":
                bot.set_config(
                    inventory_perin_converter_match_threshold=values["-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-"]
                )
                sg.user_settings_set_entry(
                    "-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-", values["-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-"]
                )
            if event == "-INVENTORY_ICONS_MATCH_THRESHOLD-":
                bot.set_config(inventory_icons_match_threshold=values["-INVENTORY_ICONS_MATCH_THRESHOLD-"])
                sg.user_settings_set_entry(
                    "-INVENTORY_ICONS_MATCH_THRESHOLD-", values["-INVENTORY_ICONS_MATCH_THRESHOLD-"]
                )

            # BOT OPTIONS - General options
            if event == "-MOBS_KILL_GOAL-":
                if values["-MOBS_KILL_GOAL-"].lower() in ["infinite", "inf", "0", ""]:
                    self.window["-MOBS_KILL_GOAL-"].update("infinite")
                    bot.set_config(mobs_kill_goal=None)
                    sg.user_settings_set_entry("-MOBS_KILL_GOAL-", "infinite")
                else:
                    try:
                        mobs_kill_goal = int(values["-MOBS_KILL_GOAL-"])
                        bot.set_config(mobs_kill_goal=mobs_kill_goal)
                        sg.user_settings_set_entry("-MOBS_KILL_GOAL-", values["-MOBS_KILL_GOAL-"])
                    except ValueError:
                        sg.cprint("Invalid mobs kill goal")
                        self.window["-MOBS_KILL_GOAL-"].update("infinite")
                        bot.set_config(mobs_kill_goal=None)
                        sg.user_settings_set_entry("-MOBS_KILL_GOAL-", "infinite")
            if event == "-FIGHT_TIME_LIMIT_SEC-":
                try:
                    fight_time_limit_sec = int(values["-FIGHT_TIME_LIMIT_SEC-"])
                    bot.set_config(fight_time_limit_sec=fight_time_limit_sec)
                    sg.user_settings_set_entry("-FIGHT_TIME_LIMIT_SEC-", values["-FIGHT_TIME_LIMIT_SEC-"])
                except ValueError:
                    sg.cprint("Invalid fight time limit")
                    self.window["-FIGHT_TIME_LIMIT_SEC-"].update("8")
                    bot.set_config(fight_time_limit_sec=8)
                    sg.user_settings_set_entry("-FIGHT_TIME_LIMIT_SEC-", "8")
            if event == "-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-":
                try:
                    delay_to_check_mob_still_alive_sec = float(values["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"])
                    bot.set_config(delay_to_check_mob_still_alive_sec=delay_to_check_mob_still_alive_sec)
                    sg.user_settings_set_entry(
                        "-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-", values["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"]
                    )
                except ValueError:
                    sg.cprint("Invalid delay to check if mob is still alive")
                    self.window["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"].update("0.25")
                    bot.set_config(delay_to_check_mob_still_alive_sec=0.25)
                    sg.user_settings_set_entry("-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-", "0.25")
            if event == "-CONVERT_PENYA_TO_PERINS_TIMER_MIN-":
                try:
                    convert_penya_to_perins_timer_min = float(values["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"])
                    bot.set_config(convert_penya_to_perins_timer_min=convert_penya_to_perins_timer_min)
                    sg.user_settings_set_entry(
                        "-CONVERT_PENYA_TO_PERINS_TIMER_MIN-", values["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"]
                    )
                except ValueError:
                    sg.cprint("Invalid convert penya to perins timer, must be in minutes")
                    self.window["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"].update("30")
                    bot.set_config(convert_penya_to_perins_timer_min=30)
                    sg.user_settings_set_entry("-CONVERT_PENYA_TO_PERINS_TIMER_MIN-", "30")

            # STATUS - Text events
            if event in self.logger_events:
                sg.cprint(values[event], c=self.logger_events_color[event])
            if event == "video_fps":
                self.window["-VIDEO_FPS-"].update(values["video_fps"])

            # MOBS - Mobs configuration
            if event == "-SELECT_MOBS-":
                print('bot.config[selected_mobs]', bot.config['selected_mobs'])
                all_mobs = bot.get_all_mobs()
                #saved_mobs_indexes = sg.user_settings_get_entry("saved_mobs_indexes", [])
                self.__select_mobs_popup(all_mobs, bot, selected_mobs_names=bot.config['selected_mobs'])
                
                #bot.set_config(selected_mobs=selected_mobs)
                #sg.user_settings_set_entry("saved_mobs_indexes", selected_mobs_indexes)
            
            if event == "-ADD_MOB-":
                self.__add_mob_popup()
                pass

            if event == "-DELETE_MOB-":
                #self.__delete_mobs_popup()
                all_mobs = bot.get_all_mobs()
                self.__select_mobs_popup(all_mobs, bot, selected_mobs_names=bot.config['selected_mobs'], is_delete_form=True)
                pass

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

    def __load_settings(self, bot):
        show_matches_text = sg.user_settings_get_entry("-SHOW_MATCHES_TEXT-", False)
        self.window["-SHOW_MATCHES_TEXT-"].update(show_matches_text)
        bot.set_config(show_matches_text=show_matches_text)

        show_mobs_pos_boxes = sg.user_settings_get_entry("-SHOW_BOXES-", False)
        self.window["-SHOW_BOXES-"].update(show_mobs_pos_boxes)
        bot.set_config(show_mobs_pos_boxes=show_mobs_pos_boxes)

        show_mobs_pos_markers = sg.user_settings_get_entry("-SHOW_MARKERS-", False)
        self.window["-SHOW_MARKERS-"].update(show_mobs_pos_markers)
        bot.set_config(show_mobs_pos_markers=show_mobs_pos_markers)

        mob_pos_match_threshold = sg.user_settings_get_entry("-MOB_POS_MATCH_THRESHOLD-", 0.7)
        self.window["-MOB_POS_MATCH_THRESHOLD-"].update(mob_pos_match_threshold)
        bot.set_config(mob_pos_match_threshold=mob_pos_match_threshold)

        mob_still_alive_match_threshold = sg.user_settings_get_entry("-MOB_STILL_ALIVE_MATCH_THRESHOLD-", 0.7)
        self.window["-MOB_STILL_ALIVE_MATCH_THRESHOLD-"].update(mob_still_alive_match_threshold)
        bot.set_config(mob_still_alive_match_threshold=mob_still_alive_match_threshold)

        mob_existence_match_threshold = sg.user_settings_get_entry("-MOB_EXISTENCE_MATCH_THRESHOLD-", 0.7)
        self.window["-MOB_EXISTENCE_MATCH_THRESHOLD-"].update(mob_existence_match_threshold)
        bot.set_config(mob_existence_match_threshold=mob_existence_match_threshold)

        inventory_perin_converter_match_threshold = sg.user_settings_get_entry(
            "-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-", 0.7
        )
        self.window["-INVENTORY_PERIN_CONVERTER_MATCH_THRESHOLD-"].update(inventory_perin_converter_match_threshold)
        bot.set_config(inventory_perin_converter_match_threshold=inventory_perin_converter_match_threshold)

        inventory_icons_match_threshold = sg.user_settings_get_entry("-INVENTORY_ICONS_MATCH_THRESHOLD-", 0.7)
        self.window["-INVENTORY_ICONS_MATCH_THRESHOLD-"].update(inventory_icons_match_threshold)
        bot.set_config(inventory_icons_match_threshold=inventory_icons_match_threshold)

        mobs_kill_goal = sg.user_settings_get_entry("-MOBS_KILL_GOAL-", "infinite")
        self.window["-MOBS_KILL_GOAL-"].update(mobs_kill_goal)
        bot.set_config(mobs_kill_goal=mobs_kill_goal if mobs_kill_goal != "infinite" else None)

        fight_time_limit_sec = sg.user_settings_get_entry("-FIGHT_TIME_LIMIT_SEC-", "8")
        self.window["-FIGHT_TIME_LIMIT_SEC-"].update(fight_time_limit_sec)
        bot.set_config(fight_time_limit_sec=fight_time_limit_sec)

        delay_to_check_mob_still_alive_sec = sg.user_settings_get_entry("-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-", "0.25")
        self.window["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"].update(delay_to_check_mob_still_alive_sec)
        bot.set_config(delay_to_check_mob_still_alive_sec=delay_to_check_mob_still_alive_sec)

        convert_penya_to_perins_timer_min = sg.user_settings_get_entry("-CONVERT_PENYA_TO_PERINS_TIMER_MIN-", "30")
        self.window["-CONVERT_PENYA_TO_PERINS_TIMER_MIN-"].update(convert_penya_to_perins_timer_min)
        bot.set_config(convert_penya_to_perins_timer_min=convert_penya_to_perins_timer_min)

        all_mobs = bot.get_all_mobs()
        # saved_mobs_indexes no more neeeded
        #saved_mobs_indexes = sg.user_settings_get_entry("saved_mobs_indexes", [])
        #selected_mobs = [all_mobs[i] for i in saved_mobs_indexes] # теперь all_mobs это дикт, по числовому индексу не найти
        selected_mobs = sg.user_settings_get_entry("saved_selected_mobs", [])
        # exist filter
        selected_mobs = [mob for mob in selected_mobs if mob in all_mobs]
        print('selected_mobs in __load_settings: ', selected_mobs)
        bot.set_config(selected_mobs=selected_mobs)

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
                        sg.Button("Add Mob", key="-ADD_MOB-"),
                        sg.Button("Delete Mob", key="-DELETE_MOB-"),
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
                        sg.InputText("infinite", size=(10, 1), enable_events=True, key="-MOBS_KILL_GOAL-"),
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
            
    def __select_mobs_popup(self, all_mobs, bot, is_delete_form=False, selected_mobs_names=[]):
        all_mobs_titles = [f"{name} - {params['element']} - {params['map_name']}" for (name, params) in dict.items(all_mobs)]
        selected_mobs_titles = [
            f"{name} - {params['element']} - {params['map_name']}" for (name, params) in dict.items(all_mobs)
            if name in selected_mobs_names
        ]
        if is_delete_form: selected_mobs_titles = []
        last_highlighted_mob = None
        exist_selected_names = [name for name in selected_mobs_names if name in all_mobs]
        print('selected_mobs_names: ', selected_mobs_names)

        popup_window = sg.Window(
            "Select Mobs" if not is_delete_form else "Delete mobs",
            [
                [sg.Text(f"Select the mobs to {'kill' if not is_delete_form else 'delete'}:")],
                [sg.Text("Find: "), sg.Input(enable_events=True, expand_x=True, key="-MOBS_SEARCH-")],
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
                [sg.Button("Reset"), sg.Button("Save" if not is_delete_form else "Delete", button_color=None if not is_delete_form else "#ea4335")],
            ],
        )
        listbox = popup_window["-MOBS_LIST-"]
        while True:
            event, values = popup_window.read()

            if event == sg.WIN_CLOSED:
                popup_window.close()
                return [], []

            if values["-MOBS_SEARCH-"] != "":
                search = values["-MOBS_SEARCH-"]
                best_match = difflib.get_close_matches(search, all_mobs_titles, n=1, cutoff=0.0)
                if last_highlighted_mob is not None:
                    listbox.Widget.itemconfigure(last_highlighted_mob, bg=listbox.BackgroundColor)
                    last_highlighted_mob = None
                if len(best_match) > 0:
                    best_match_index = all_mobs_titles.index(best_match[0])
                    listbox.Widget.itemconfigure(best_match_index, bg=hex_variant(listbox.BackgroundColor, -20))
                    listbox.update(scroll_to_index=best_match_index)
                    last_highlighted_mob = best_match_index
            else:
                if last_highlighted_mob is not None:
                    listbox.Widget.itemconfigure(last_highlighted_mob, bg=listbox.BackgroundColor)
                    last_highlighted_mob = None

            if event == "-MOBS_LIST-" and len(values["-MOBS_LIST-"]):
                print('values[-MOBS_LIST-]', values["-MOBS_LIST-"])
                # values["-MOBS_LIST-"] = ['aibat - flaris - water']
                selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in values["-MOBS_LIST-"]]
                #selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in values["-MOBS_LIST-"]]
                listbox.update(set_to_index=selected_mobs_indexes)

            if event == "Reset":
                listbox.update(set_to_index=[])
            if event == "Save":
                selected_mobs_indexes = [all_mobs_titles.index(mob) for mob in values["-MOBS_LIST-"]]
                popup_window.close()
                names = list(dict.keys(all_mobs))
                sg.user_settings_set_entry("saved_selected_mobs", [names[i] for i in selected_mobs_indexes])
                bot.set_config(selected_mobs=[names[i] for i in selected_mobs_indexes])
                return [names[i] for i in selected_mobs_indexes], selected_mobs_indexes
            if event == "Delete":
                from assets.Assets import MobInfo
                deleted_mobs_names = [mob.split('-')[0].strip() for mob in values["-MOBS_LIST-"]]
                popup_window.close()
                # unselect deleted mobs if they were selected
                bot.set_config(selected_mobs=[name for name in exist_selected_names if name not in deleted_mobs_names])
                MobInfo.delete_mobs(deleted_mobs_names)
                pass
    
    def __add_mob_popup(self):
        from assets.Assets import mob_type_wind_path, mob_type_fire_path, mob_type_soil_path, mob_type_water_path, mob_type_electricity_path

        element_buttons_layout = [
            sg.Text("Select mob element: "),
            sg.Input(key="-ELEMENT-", visible=False), # hidden controlled input
            sg.Button("", image_source=mob_type_wind_path, key="-ELEMENT-WIND-"),
            sg.Button("", image_source=mob_type_fire_path, key="-ELEMENT-FIRE-"),
            sg.Button("", image_source=mob_type_soil_path, key="-ELEMENT-SOIL-"),
            sg.Button("", image_source=mob_type_water_path, key="-ELEMENT-WATER-"),
            sg.Button("", image_source=mob_type_electricity_path, key="-ELEMENT-ELECTRICITY")
        ]

        popup_window = sg.Window(
            "Add mob",
            [
                [sg.Text("Enter mob name: "), sg.Input(key="-NAME-", size=(48,20))],
                [sg.Text("Enter map name (location): "), sg.Input(key="-MAP-", size=(40,20))],
                [
                    sg.Text("Choose an image file (mob name): "),
                    sg.Input(key="-IMAGE-", change_submits=True, size=(25, 20), disabled=True, text_color="#000"),
                    sg.FileBrowse(file_types=(('Image files', '*.png *.jpg *.jpeg'),))
                ],
                [sg.Text("Enter height offset: "), sg.Input(key="-HEIGHT-", enable_events=True, size=(10,20)), sg.Text("(Number, usually in range from 40 to 100)", text_color="grey")],
                element_buttons_layout,
                [sg.Frame('', [[sg.Button("Reset"), sg.Button("Save")]], border_width=0, pad=((0, 0),(44, 0)))],
            ],
            modal=True,
            size=(500, 225)
        )

        while True:
            event, values = popup_window.read()
            print('event: ', event, values)

            if event == sg.WIN_CLOSED:
                popup_window.close()
                return
            if event == "Reset":
                for elem in element_buttons_layout:
                     if elem.Disabled: elem.update(disabled=False)

                for value in values:
                    if value.startswith('-'):
                        popup_window.Element(value).update('')
                pass
            if event == "Save":
                # form validation
                is_form_valid = True
                for key in ['-NAME-', '-MAP-', '-IMAGE-', '-HEIGHT-', '-ELEMENT-']:
                    if not len(values[key]):
                        is_form_valid = False
                        break

                if is_form_valid:
                    from assets.Assets import MobInfo
                    MobInfo.add_new_mob(name=values["-NAME-"], map_name=values["-MAP-"], image_path=values["-IMAGE-"],
                                        height_offset=int(values["-HEIGHT-"]), element=values["-ELEMENT-"])
                    popup_window.close()
                    return
            if event == "-HEIGHT-":
                # height validation - only numbers
                popup_window.Element(event).update(re.sub('[^0-9]','', values['-HEIGHT-']))
                pass
            if "-ELEMENT-" in event:
                current_element = event.split('-')[2].lower()

                for elem in element_buttons_layout:
                     if elem.Disabled: elem.update(disabled=False)
                popup_window.Element(event).update(disabled=True)

                popup_window.Element('-ELEMENT-').update(current_element)
                pass
        pass
