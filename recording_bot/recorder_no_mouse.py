from pynput import mouse, keyboard
from time import time
import json
import os


OUTPUT_FILENAME = 'tower_b5'
# declare our start_time globally so that the callback functions can reference it
start_time = None
# keep track of unreleased keys to prevent over-reporting press events
unreleased_keys = []
# storing all input events
input_events = []

class EventType():
	KEYDOWN = 'keyDown'
	KEYUP = 'keyUp'


def main():
	runListeners()
	print("Recording duration: {} seconds".format(elapsed_time()))
	global input_events
	print(json.dumps(input_events))

	# write the output to a file
	script_dir = os.path.dirname(__file__)
	filepath = os.path.join(
		script_dir, 
		'recordings', 
		'{}.json'.format(OUTPUT_FILENAME)
	)
	with open(filepath, 'w') as outfile:
		json.dump(input_events, outfile, indent=4)


def elapsed_time():
	global start_time
	return time() - start_time


def record_event(event_type, event_time, button):
	global input_events
	input_events.append({
		'time': event_time,
		'type': event_type,
		'button': str(button)
	})
	print('{} on {} at {}'.format(event_type, button, event_time))


def on_press(key):
	# we only want to record the first keypress event until that key has been 
	# released
	global unreleased_keys
	if key in unreleased_keys:
		return
	else:
		unreleased_keys.append(key)

	try:
		record_event(EventType.KEYDOWN, elapsed_time(), key.char)
	except AttributeError:
		record_event(EventType.KEYDOWN, elapsed_time(), key)


def on_release(key):
	# mark key as no longer pressed
	global unreleased_keys
	try:
		unreleased_keys.remove(key)
	except ValueError:
		print('ERROR: {} not in unreleased_keys'.format(key))

	try:
		record_event(EventType.KEYUP, elapsed_time(), key.char)
	except AttributeError:
		record_event(EventType.KEYUP, elapsed_time(), key)

	# stop listener with the escape key
	if key == keyboard.Key.esc:
		# Stop keyboard listener
		raise keyboard.Listener.StopException


def runListeners():
	# Collect keyboard inputs until released
	# https://pynput.readthedocs.io/en/latest/keyboard.html#monitoring-the-keyboard
	with keyboard.Listener(
			on_press=on_press, 
			on_release=on_release) as listener:
		global start_time
		start_time = time()
		listener.join()


if __name__ == "__main__":
	main()