import os
import json
import win32api, win32con, win32gui
from time import sleep, time
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener
from ctypes import windll


def main():
	hwnd = get_focused_window_handle()
	start_countdown(3)

	playActions("tower_b5.json", hwnd)
	sleep(1)
	print("Done")


def playActions(filename, hwnd):
	# Read the file
	script_dir = os.path.dirname(__file__)
	filepath = os.path.join(
		script_dir, 
		'recordings', 
		filename
	)
	with open(filepath, 'r') as jsonfile:
		# parse the json
		data = json.load(jsonfile)
		
		# loop over each action
		# Because we are not waiting any time before executing the first action, any delay before the initial
		# action is recorded will not be reflected in the playback.
		for index, action in enumerate(data):
			action_start_time = time()

			# look for escape input to exit
			if action['button'] == 'Key.esc':
				break

			# perform the action
			if action['type'] == 'keyDown':
				key = convertKey(action['button'])
				window_key_down(hwnd, key)
				print("keyDown on {}".format(key))
			elif action['type'] == 'keyUp':
				key = convertKey(action['button'])
				window_key_up(hwnd, key)
				print("keyUp on {}".format(key))
			elif action['type'] == 'click':
				magic_click(hwnd, action['pos'][0], action['pos'][1])
				#right_click_window(hwnd, action['pos'][0], action['pos'][1])
				print("click on {}".format(action['pos']))

			# then sleep until next action should occur
			try:
				next_action = data[index + 1]
			except IndexError:
				# this was the last action in the list
				break
			elapsed_time = next_action['time'] - action['time']

			# if elapsed_time is negative, that means our actions are not ordered correctly. throw an error
			if elapsed_time < 0:
				raise Exception('Unexpected action ordering.')

			# adjust elapsed_time to account for our code taking time to run
			elapsed_time -= (time() - action_start_time)
			if elapsed_time < 0:
				elapsed_time = 0
			print('sleeping for {}'.format(elapsed_time))
			sleep(elapsed_time)


# convert pynput button keys into win32 virtual keys
# https://pynput.readthedocs.io/en/latest/_modules/pynput/keyboard/_base.html#Key
# https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
def convertKey(button):
	PYNPUT_SPECIAL_CASE_MAP = {
		'f1': 0x70,
		'f2': 0x71,
		'f3': 0x72,
		'f4': 0x73,
		'f5': 0x74,
		'f6': 0x75,
		'f7': 0x76,
		'f8': 0x77,
		'f9': 0x78,
		'space': 0x20,
		'enter': 0x0D,
		'w': 0x57,
		'a': 0x41,
		's': 0x53,
		'd': 0x44,
		'c': 0x43,
		'up': 0x26,
		'left': 0x25,
		'down': 0x28,
		'right': 0x27,
		'1': 0x30,
		'2': 0x31,
		'3': 0x32,
		'4': 0x33,
		'5': 0x34,
		'6': 0x35,
		'7': 0x36,
		'8': 0x37,
		'9': 0x38,
	}

	# example: 'Key.F9' should return 'F9', 'w' should return as 'w'
	cleaned_key = button.replace('Key.', '')

	if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
		return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]

	return cleaned_key


def get_focused_window_handle():
	print('\nClick in the window to get the process! The first click will be considered.')

	hwnd = []

	def on_click(x, y, button, pressed):
		if not pressed:
			hwnd.append(win32gui.GetForegroundWindow())
			return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	print('Window Selected: ', win32gui.GetWindowText(hwnd[0]))
	sleep(0.5)
	return hwnd[0]


def window_key_down(hwnd, key):
	win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0);


def window_key_up(hwnd, key):
	win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0);


def magic_click(hwnd, x, y):
	old_pos = win32api.GetCursorPos()
	windll.user32.BlockInput(True)
	win32api.SetCursorPos((x, y))
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
	sleep(0.005)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, 0)
	sleep(0.015)
	win32api.SetCursorPos(old_pos)
	windll.user32.BlockInput(False)


def right_click_window(hwnd, x, y):
	lParam = win32api.MAKELONG(x, y)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
	sleep(0.005)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)


# region Helpers
def start_countdown(sleep_time_sec=5):
    print('Starting', end='', flush=True)
    for i in range(10):
        print('.', end='', flush=True)
        sleep(sleep_time_sec/10)
    print('\nReady, forcing dwarves to work!')


def print_logo(text_logo: str):
    figlet = Figlet(font='slant')
    print(figlet.renderText(text_logo))
# endregion

if __name__ == "__main__":
    try:
        print_logo('Background Playback Bot')
        main()
    except Exception as e:
        print(str(e))
