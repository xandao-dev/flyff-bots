import time
from collections import deque

import win32gui
from pyfiglet import Figlet


def get_window_handlers():
    hwnd_from_title = {}
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd) != "":
            hwnd_from_title[win32gui.GetWindowText(hwnd)] = hwnd
            print(hex(hwnd), win32gui.GetWindowText(hwnd))

    win32gui.EnumWindows(winEnumHandler, None)
    return hwnd_from_title

i = 0
def get_point_near_center(center, points):
    dist_two_points = lambda center, point: ((center[0] - point[0]) ** 2 + (center[1] - point[1]) ** 2) ** (1 / 2)
    closest_dist = 999999  # Start with a big number for smaller search
    best_point = deque(maxlen=2)
    for point in points:
        dist = dist_two_points(center, point)
        if dist < closest_dist:
            closest_dist = dist
            best_point.append(point)
    # Return the second most nearest point or the nearest point if just have one point.
    # Because the nearest mob sometimes is already dead and we don't want to select it.
    global i
    if i == 0:
        i = -1
    elif i == -1:
        i = 0
    return best_point[i]


def start_countdown(voice_engine, sleep_time_sec=5):
    if not voice_engine.isBusy():
        voice_engine.say(f"Starting in {sleep_time_sec} seconds")
        voice_engine.runAndWait()
    print("Starting", end="")
    for i in range(10):
        print(".", end="")
        time.sleep(sleep_time_sec / 10)
    print("\nReady, forcing dwarves to work!")


def print_logo(text_logo: str):
    figlet = Figlet(font="slant")
    print(figlet.renderText(text_logo))

def hex_variant(hex_color, brightness_offset=1):
    """ 
        Takes a color like #87c95f and produces a lighter(+) or darker(-) variant.
        Is not the best way to do this, because it does not take into account the luminance of the color.
    """
    if len(hex_color) != 7:
        raise Exception("Passed %s into color_variant(), needs to be in #87c95f format." % hex_color)
    rgb_hex = [hex_color[x:x+2] for x in [1, 3, 5]]
    new_rgb_int = [int(hex_value, 16) + brightness_offset for hex_value in rgb_hex]
    new_rgb_int = [min([255, max([0, i])]) for i in new_rgb_int] # make sure new values are between 0 and 255
    # hex() produces "0x88", we want just "88"
    return "#" + "".join([hex(i)[2:] for i in new_rgb_int])