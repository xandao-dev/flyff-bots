from time import sleep
from collections import deque

import win32gui
from pyfiglet import Figlet
from pynput.mouse import Listener as MouseListener


def get_focused_window_handle(voice_engine):
	print('\nClick in the flyff window to get the process! The first click will be considered.')
	voice_engine.say('Selecione a tela do jogo')

	hwnd = []

	def on_click(x, y, button, pressed):
		if not pressed:
			hwnd.append(win32gui.GetForegroundWindow())
			return False

	voice_engine.runAndWait()
	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	print('Window Selected: ', win32gui.GetWindowText(hwnd[0]))
	sleep(0.5)
	return hwnd[0]


i=0
def get_point_near_center(center, points):
	dist_two_points = lambda center, point : ((center[0] - point[0])**2 + (center[1] - point[1])**2)**(1/2)
	closest_dist = 999999 #Start with a big number for smaller search
	best_point = deque(maxlen=2)
	for point in points:
		dist = dist_two_points(center, point)
		if dist < closest_dist:
			closest_dist = dist
			best_point.append(point)
	# Return the second most nearest point or the nearest point if just have one point.
	# Because the nearest mob sometimes is already dead and we don't want to select it.
	global i
	if i == 0: i = -1
	elif i == -1: i = 0
	return best_point[i]


def start_countdown(voice_engine, sleep_time_sec=5):
	voice_engine.say(f'Iniciando em {sleep_time_sec} segundos')
	voice_engine.runAndWait()
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		sleep(sleep_time_sec/10)
	print('\nReady, forcing dwarves to work!')


def print_logo(text_logo: str):
	figlet = Figlet(font='slant')
	print(figlet.renderText(text_logo))
