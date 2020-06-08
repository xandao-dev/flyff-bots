# region Imports
import time
import re
import ctypes
from pathlib import Path

from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string
from PIL import Image
import keyboard
import pyautogui
import win32api
import win32con
# endregion


def main(debug=False):
	print('\nHold "q" to stop the bot.')

	enemy_life_pixel = get_enemy_life_pixel()
	battle_area_pos = get_battle_area_pos(use_coordinates=True)
	for x in range(battle_area_pos[0], battle_area_pos[2], 25):
		for y in range(battle_area_pos[1], battle_area_pos[3], 25):
			move_mouse(x, y)
			time.sleep(0.01)
			#print(pixel(x, y))
			if match_pixel(
					enemy_life_pixel[0],
					enemy_life_pixel[1],
					enemy_life_pixel[2]):
				pyautogui.doubleClick(x, y)
				break
		else:
			continue  # only executed if the inner loop did NOT break
		break  # only executed if the inner loop DID break


# region Mouse
def get_char_head_pos():
    print('\nClick in the top of the head of the char! The first click will be considered.')

    char_head_pos = []

    def on_click(x, y, button, pressed):
        if pressed:
            char_head_pos.extend((x, y))
        if not pressed:
            return False

    with MouseListener(on_click=on_click) as mouse_listener:
        mouse_listener.join()

    return char_head_pos


def get_enemy_life_area_pos():
    print("\nSelect the top-left corner of the enemy life, then select the " +
          "bottom-right corner.\nThe two first clicks will be considered.")

    enemy_life_area_pos = []
    is_first_click = [True]

    def on_click(x, y, button, pressed):
        if pressed:
            if is_first_click[0]:
                enemy_life_area_pos.extend((x, y))
                is_first_click[0] = False
            else:
                width = x - enemy_life_area_pos[0]
                height = y - enemy_life_area_pos[1]
                enemy_life_area_pos.extend((width, height))
                return False

    with MouseListener(on_click=on_click) as mouse_listener:
        mouse_listener.join()

    time.sleep(0.5)
    return enemy_life_area_pos


def get_enemy_life_pixel():
    """Get enemy life(red bar) pixel position and color

    Returns:
            List: 0-> x, 1-> y, 2-> color
    """
    print('\nClick inside the life enemy life to get the pixel color.')

    enemy_life_pixel = []

    def on_click(x, y, button, pressed):
        if pressed:
            enemy_life_pixel.extend((x, y, pixel(x, y)))
        if not pressed:
            return False

    with MouseListener(on_click=on_click) as mouse_listener:
        mouse_listener.join()

    time.sleep(0.5)
    return enemy_life_pixel


def get_battle_area_pos(use_coordinates=False):
    print("\nSelect the top-left corner of the battle area, then select the " +
          "bottom-right corner.\nThe two first clicks will be considered.")

    battle_area_pos = []
    is_first_click = [True]

    def on_click(x, y, button, pressed):
        if pressed:
            if is_first_click[0]:
                battle_area_pos.extend((x, y))
                is_first_click[0] = False
            else:
                if not use_coordinates:
                    width = x - battle_area_pos[0]
                    height = y - battle_area_pos[1]
                    battle_area_pos.extend((width, height))
                else:
                    battle_area_pos.extend((x, y))
                return False

    with MouseListener(on_click=on_click) as mouse_listener:
        mouse_listener.join()

    time.sleep(0.5)
    return battle_area_pos


def get_cursor_type():
    # Argument structures
    class POINT(ctypes.Structure):
        _fields_ = [('x', ctypes.c_int),
                    ('y', ctypes.c_int)]

    class CURSORINFO(ctypes.Structure):
        _fields_ = [('cbSize', ctypes.c_uint),
                    ('flags', ctypes.c_uint),
                    ('hCursor', ctypes.c_void_p),
                    ('ptScreenPos', POINT)]

    # Load function from user32.dll and set argument types
    GetCursorInfo = ctypes.windll.user32.GetCursorInfo
    GetCursorInfo.argtypes = [ctypes.POINTER(CURSORINFO)]

    # Initialize the output structure
    info = CURSORINFO()
    info.cbSize = ctypes.sizeof(info)

    if GetCursorInfo(ctypes.byref(info)):
        print(info.hCursor)
    else:
        pass  # Error occurred (invalid structure size?)


def move_mouse(x, y):
    win32api.SetCursorPos((x, y))


def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
# endregion


# region Helpers
def pixel(x, y):
    """
    #PARA RGB
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
    r = color % 256
    g = (color // 256) % 256
    b = color // (256 ** 2)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return (r, g, b)
    """
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return color


def match_pixel(x, y, color_to_match):
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    #print(f'color_to_match: {color_to_match}, color: {color}')
    return color-10 <= color_to_match and color+10 >= color_to_match


def get_circles(radius, border):
    circles = []
    for x in range(round(radius*2)):
        for y in range(round(radius*2)):
            circle_eq = round((x-radius)**2 + (y-radius)**2)
            if circle_eq >= (radius**2 - border) and circle_eq <= (radius**2 + border):
                circles.append((x, y))
    return circles


def start_countdown(sleep_time_sec=5):
    print('Starting', end='')
    for i in range(10):
        print('.', end='')
        time.sleep(sleep_time_sec/10)
    print('\nReady,forcing gnomes to work hard!')


def print_logo(text_logo: str):
    figlet = Figlet(font='slant')
    print(figlet.renderText(text_logo))
# endregion


if __name__ == '__main__':
    try:
        print_logo('Flyff Farm Bot')
        main()
    except Exception as e:
        print(str(e))
