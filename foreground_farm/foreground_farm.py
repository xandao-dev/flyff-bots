"""Foreground Farm

Farm aproach: Move the mouse in the screen and watch if the enemy life's bar appears, then
click in the mob and atack it. Doesn't work very well.
"""

# region Imports
import time
from pathlib import Path
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
import keyboard
from pytesseract import image_to_string
from PIL import Image
import pyautogui
import win32api
import win32con
# endregion


# Notas: objetos longes precisam ser analisados em um intervalo de pixel menor(10+-) 
# e também precisam de um delay para o mouse não passar do ponto
def main(debug=False):
	enemy_life_pixel = get_enemy_life_pixel()
	x_battle, y_battle, x1_battle, y1_battle = get_battle_area_pos(use_coordinates=True)
	for x in range(x_battle, x1_battle, 20):
		for y in range(y_battle, y1_battle, 20):
			time.sleep(0.01)
			move_cursor(x, y)
			if pyautogui.pixelMatchesColor(
					enemy_life_pixel[0],
					enemy_life_pixel[1],
					enemy_life_pixel[2],
					3):
				print('Mob found!')
				right_click(x, y, True)
				keyboard.press('F1')
				break
		else:
			continue  # only executed if the inner loop did NOT break
		break  # only executed if the inner loop DID break


def get_enemy_life_pixel():
    """Get enemy life(red bar) pixel position and color

    Returns:
            List: 0-> x, 1-> y, 2-> (rbg)
    """
    print('\nClick inside the life enemy life to get the pixel color.')

    enemy_life_pixel = []

    def on_click(x, y, button, pressed):
        if pressed:
            enemy_life_pixel.extend((x, y, pyautogui.pixel(x, y)))
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


def move_cursor(x, y):
    win32api.SetCursorPos((x, y))


def right_click(x, y, set_position=True):
	if set_position:
		win32api.SetCursorPos((x, y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def double_right_click(x, y, set_position=True):
	if set_position:
		win32api.SetCursorPos((x, y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# region Helpers
def start_countdown(sleep_time_sec=5):
    print('Starting', end='')
    for i in range(10):
        print('.', end='')
        time.sleep(sleep_time_sec/10)
    print('\nReady, forcing gnomes to work hard!')


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
