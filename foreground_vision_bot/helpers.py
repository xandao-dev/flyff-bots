from sleep import sleep
from pyfiglet import Figlet


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