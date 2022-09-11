import PySimpleGUI as sg
import cv2

def main():
    sg.theme('DarkAmber')
    layout = [
        [sg.Text("Flyff Farm Bot", font='Any 18')],
        [sg.Checkbox("Show bot's vision", False, key="-SHOW_VISION-")],
        [sg.Image(filename="", key="-DEBUG_IMAGE-")],
        [sg.Button("Start", size=(10, 1)), sg.Button("Exit", size=(10, 1))],
    ]

    # Create the window and show it without the plot
    window = sg.Window("Flyff FVB", layout, location=(800, 400), resizable=True)

    cap = cv2.VideoCapture(0)

    while True:
        event, values = window.read(timeout=20)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        ret, frame = cap.read()

        if values["-SHOW_VISION-"]:
            imgbytes = cv2.imencode(".png", frame)[1].tobytes()
            window["-DEBUG_IMAGE-"].update(data=imgbytes)
        else:
            window["-DEBUG_IMAGE-"].update(data=None)

    window.close()


if __name__ == "__main__":
    main()
