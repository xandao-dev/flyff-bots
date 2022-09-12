import PySimpleGUI as sg
import cv2 as cv


class Gui:
    def __init__(self, theme="DarkAmber"):
        self.printable_events = ["msg", "msg_red", "msg_purple", "msg_blue"]
        self.printable_events_color = {
            "msg": ("white", "black"),
            "msg_red": ("white", "red"),
            "msg_purple": ("white", "purple"),
            "msg_blue": ("white", "blue"),
        }
        sg.theme(theme)

    def __get_layout(self):
        title = [sg.Text("Flyff FVF", font="Any 18")]

        main = sg.Column(
            [
                [
                    sg.Frame(
                        "Options:",
                        [
                            [sg.Checkbox("Show bot's vision", False, enable_events=True, key="-SHOW_FRAMES-")],
                            [sg.Checkbox("Show boxes", False, disabled=True, enable_events=True, key="-SHOW_BOXES-")],
                            [sg.Checkbox("Show markers", False, disabled=True, enable_events=True, key="-SHOW_MARKERS-")],
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
                            [
                                sg.Text("Delay to check if mob is still alive (s):")
                            ],
                            [
                                sg.InputText("0.25", size=(10, 1), key="-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"),
                            ]
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
        )

        video = sg.Column(
            [
                [
                    sg.Frame(
                        "Bot's Vision:",
                        [[sg.Image(filename="", key="-DEBUG_IMAGE-")]],
                    )
                ]
            ],
            pad=(0, 0),
        )

        footer = sg.Column(
            [
                [
                    sg.Frame(
                        "Actions:",
                        [
                            [
                                sg.Column(
                                    [[sg.Button("Attach Window"), sg.Button("Start", disabled=True, key="-START_BOT-"), sg.Button("Exit")]],
                                    pad=(0, 0),
                                )
                            ]
                        ],
                    )
                ]
            ],
            pad=(0, 0),
        )

        return [title, [main, video], [footer]]

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
                        self.window['-MOBS_KILL_GOAL-'].update("infinity")
                        bot.set_config(mobs_kill_goal=None)
            if event == "-FIGHT_TIME_LIMIT_SEC-":
                try:
                    fight_time_limit_sec = int(values["-FIGHT_TIME_LIMIT_SEC-"])
                    bot.set_config(fight_time_limit_sec=fight_time_limit_sec)
                except ValueError:
                    sg.cprint("Invalid fight time limit")
                    self.window['-FIGHT_TIME_LIMIT_SEC-'].update("8")
                    bot.set_config(fight_time_limit_sec=8)
            if event == "-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-":
                try:
                    delay_to_check_mob_still_alive_sec = float(values["-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-"])
                    bot.set_config(delay_to_check_mob_still_alive_sec=delay_to_check_mob_still_alive_sec)
                except ValueError:
                    sg.cprint("Invalid delay to check if mob is still alive")
                    self.window['-DELAY_TO_CHECK_MOB_STILL_ALIVE_SEC-'].update("0.25")
                    bot.set_config(delay_to_check_mob_still_alive_sec=0.25)
            if values["-SHOW_FRAMES-"]:
                img = values.get("image_mobs_position", None)
                if img is not None:
                    imgbytes = cv.imencode(".png", img)[1].tobytes()
                    self.window["-DEBUG_IMAGE-"].update(data=imgbytes)

            if event in self.printable_events:
                sg.cprint(values[event], c=self.printable_events_color[event])

    def close(self):
        self.window.close()
