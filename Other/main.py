from pyfiglet import Figlet
from pynput.keyboard import Key, Controller
import time


def main():
	keyboard = Controller()
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		time.sleep(0.5)
	print('\nG0!')
	keyboard.press('w')
	time.sleep(2)
	keyboard.release('w')


def print_logo(text_logo: str):
    figlet = Figlet(font='slant')
    print(figlet.renderText(text_logo))


if __name__ == '__main__':
	try:
		print_logo('Flyff Bot')
		main()
	except Exception as e:
		print(str(e))