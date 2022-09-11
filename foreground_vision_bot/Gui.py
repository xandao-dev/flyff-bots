import PySimpleGUI as sg
import sys


class Gui:
    def __init__(self, theme="DarkAmber"):
        sg.theme(theme)

    def init(self):
        layout = [
            [sg.Text("Flyff FVF", font="Any 18")],
            [sg.Checkbox("Show bot's vision", False, key="-SHOW_VISION-")],
            [sg.Image(filename="", key="-DEBUG_IMAGE-")],
            [sg.Button("Start", size=(10, 1)), sg.Button("Exit", size=(10, 1))],
        ]

        self.window = sg.Window("Flyff FVF", layout, location=(800, 400), resizable=True, finalize=True)
        return self.window

    def update(self, *, imgbytes):
        event, values = self.window.read(timeout=20)

        if event == "Exit" or event == sg.WIN_CLOSED:
            self.close()
            sys.exit()

        if values["-SHOW_VISION-"]:
            # imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            self.window["-DEBUG_IMAGE-"].update(data=imgbytes)
        else:
            self.window["-DEBUG_IMAGE-"].update(data=None)

        return {
            "show_vision": values["-SHOW_VISION-"],
        }

    def close(self):
        self.window.close()
