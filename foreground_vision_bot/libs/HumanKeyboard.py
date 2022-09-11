import win32api, win32con
from time import sleep, time
from random import randint, uniform


VKEY = {
	'a': 0x41,
	'd': 0x44,
	'w': 0x57,
	's': 0x53,
}

class HumanKeyboard:
	def __init__(self, hwnd):
		self.hwnd = hwnd

	# Keys: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
	# Smallest press_time = 0.015
	def press_key(self, key, stop_when_w=True, press_time=0.015):
		# 1/0.015-> Time average for each iteration
		for i in range(round(press_time*(1/0.015))):
			win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, key, 0)
			sleep(0.005)
			win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, key, 0)
			sleep(0.01)
			
		#Stop auto run
		if key == VKEY['w'] and stop_when_w:
			win32api.PostMessage(self.hwnd, win32con.WM_KEYDOWN, VKEY['s'], 0)
			sleep(0.005)
			win32api.PostMessage(self.hwnd, win32con.WM_KEYUP, VKEY['s'], 0)
			sleep(0.01)

	def human_turn_back(self):
		keys = (VKEY['a'], VKEY['d'])
		random_time = round(uniform(0.6, 0.8), 3)
		self.press_key(VKEY['w'], stop_when_w=False, press_time=0.06)
		self.press_key(keys[randint(0, len(keys) - 1)], press_time=random_time)
		self.press_key(VKEY['s'])