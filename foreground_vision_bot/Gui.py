import PySimpleGUI as sg
import cv2 as cv


class Gui:
    def __init__(self, theme="DarkAmber"):
        self.printable_events = ['msg', 'msg_red', 'msg_purple', 'msg_blue']
        self.printable_events_color = {'msg':('white', 'black'), 'msg_red':('white', 'red'), 'msg_purple':('white', 'purple'), 'msg_blue':('white', 'blue')}
        sg.theme(theme)

    def init(self):
        layout = [
            [sg.Text("Flyff FVF", font="Any 18")],
            [sg.Checkbox("Show bot's vision", False, change_submits=True, enable_events=True, key="-SHOW_FRAMES-")],
            [sg.Checkbox("Show boxes", False, change_submits=True, enable_events=True, key="-SHOW_BOXES-")],
            [sg.Checkbox("Show markers", False, change_submits=True, enable_events=True, key="-SHOW_MARKERS-")],
            [sg.Image(filename="", key="-DEBUG_IMAGE-")],
            [sg.Text('', size=(15, 1), key='-OUTPUT-')],
            [sg.Multiline(size=(40, 26), key='-ML-', autoscroll=True)],
            [sg.Button("Start", size=(10, 1)), sg.Button("Exit", size=(10, 1))],
        ]

        self.window = sg.Window("Flyff FVF", layout, location=(800, 400), resizable=True, finalize=True)
        sg.cprint_set_output_destination(self.window, '-ML-')
        return self.window

    def loop(self, bot):
        while True:
            event, values = self.window.read(timeout=1000)

            if event == "Exit" or event == sg.WIN_CLOSED:
                break

            if event == "-SHOW_FRAMES-":
                bot.set_config(show_frames=values["-SHOW_FRAMES-"])
                if not values["-SHOW_FRAMES-"]:
                    self.window["-DEBUG_IMAGE-"].update(data=None)

            if event == "-SHOW_BOXES-":
                bot.set_config(show_mobs_pos_boxes=values["-SHOW_BOXES-"])

            if event == "-SHOW_MARKERS-":
                bot.set_config(show_mobs_pos_markers=values["-SHOW_MARKERS-"])

            if values["-SHOW_FRAMES-"]:
                img = values.get('image_mobs_position', None)
                if img is not None:
                    imgbytes = cv.imencode(".png", img)[1].tobytes()
                    self.window["-DEBUG_IMAGE-"].update(data=imgbytes)

            if event in self.printable_events:
                sg.cprint(values[event], c=self.printable_events_color[event])

    def close(self):
        self.window.close()
