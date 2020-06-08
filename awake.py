#region Imports
import time
import re
from pathlib import Path

from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from pytesseract import image_to_string
from PIL import Image
import keyboard
import pyautogui
import win32api
import win32con
#endregion

"""
STATS

Max. HP +(50 - 500)
Max. MP +(50 - 450)
Max. FP +(50 - 500)
STR +(5 - 35)
STA +(5 - 35)
DEX +(5 - 35)
INT +(5 - 35) 
Attack +(5 - 140)
DEF +(4 - 112)
Speed +(1 - 10)%
Attack Speed +(2 - 38)%
Critical Chance +(1 - 10)%
Additional Damage of Critical Hits +(1 - 19)%
Decreased Casting Time +(1 - 10)%
"""

awakening_interval = 0.95

def main(debug=False):
	attribute = input('What is the attribute? ')
	attribute2 = input('What is the attribute 2? ')
	min_value = int(input('What is the minimum value? '))
	start_awake_button_pos = get_start_awake_button_pos()
	awake_area_pos = get_awake_area_pos()
	start_countdown(3)

	print('\nHold "q" to stop the bot.')
	while keyboard.is_pressed('q') == False:
		#take a screenshot and convert to black/white
		awake_area = pyautogui.screenshot(region=(awake_area_pos)).convert('1', dither=Image.NONE)

		if debug:
			#save screenshot to debug
			awake_area.save(Path(__file__).parent/"awake.png") 

		#get text and split in array
		awake_text_list = image_to_string(awake_area, lang='eng').split('\n')

		#Delete empty strings
		awake_text_list = [i for i in awake_text_list if i.strip()]  

		#Print the awake list
		print(', '.join(awake_text_list))

		# Search for the awake
		for awake in awake_text_list:
			if attribute in awake or attribute2 in awake:
				attr_value = int(re.findall('\d+', awake)[0])
				if min_value <= attr_value:
					print(f'\nFound: {awake}\n')
					exit()

		#click in awake button
		click(*start_awake_button_pos)
		time.sleep(awakening_interval)


# region Mouse
def get_start_awake_button_pos():
	print('\nClick in the "start" awakening button! The first click will be considered.')
	
	start_awake_button_pos = []
	def on_click(x, y, button, pressed):
		if pressed:
			start_awake_button_pos.extend((x, y))
		if not pressed:
			return False
	
	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	return start_awake_button_pos


def get_awake_area_pos():
	print("\nSelect the top-left corner of the white awakening area, then select the " +
	"bottom-right corner.\nThe two first clicks will be considered.")
	
	awake_area_pos = []
	is_first_click = [True]
	def on_click(x, y, button, pressed):
		if pressed:
			if is_first_click[0]:
				awake_area_pos.extend((x, y))
				is_first_click[0] = False
			else:
				width = x - awake_area_pos[0]
				height = y - awake_area_pos[1]
				awake_area_pos.extend((width, height))
				return False
	
	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	return awake_area_pos


def click(x,y):
	win32api.SetCursorPos((x,y))
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,0,0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,0,0)
# endregion


# region Helpers
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
        print_logo('Flyff Awakening Bot')
        main()
    except Exception as e:
        print(str(e))
