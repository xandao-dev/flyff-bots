import pyautogui
import ctypes
import time
from PIL import Image, ImageFilter
from ctypes import windll
from pyfiglet import Figlet
from pytesseract import image_to_string
from pynput.mouse import Listener as MouseListener
from pathlib import Path
import cv2 as cv
import numpy as np

# install pywin32 to use these modules and execute the installer in Scripts folder
# https://github.com/mhammond/pywin32
import win32api  # subpackage of pywin32
import win32con  # subpackage of pywin32
import win32gui  # subpackage of pywin32
import win32ui  # subpackage of pywin32

# Wait for two click in screen to get the region(x, y, width, height). use_coordinate to return (x, y, cx, cy).
# Library: from pynput.mouse import Listener as MouseListener, time
def get_region(use_coordinates=False):
	print("\nSelect the top-left corner of area, then select the " +
		  "bottom-right corner.\nThe two first clicks will be considered.")

	region = []
	is_first_click = [True]

	def on_click(x, y, button, pressed):
		if pressed:
			if is_first_click[0]:
				region.extend((x, y))
				is_first_click[0] = False
			else:
				if not use_coordinates:
					width = x - region[0]
					height = y - region[1]
					region.extend((width, height))
				else:
					region.extend((x, y))
				return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	time.sleep(0.5)
	return region


# Take Screenshot (PIL Image) and save to a path. pyautogui is very slow.
# Library: pyautogui, pathlib.Path
def screenshot(region=None):
	# region, first fixel then width and height
	if not region:
		region = (0, 0, pyautogui.size()[0], pyautogui.size()[1])
	img = pyautogui.screenshot(region=region)
	img.save('screenshot.png')
	return img


# Right Click on screen based on X and Y coordinates. Very Fast.
# Library: pywin32 -> import win32api, pywin32 -> import win32con
def right_click(x, y):
	win32api.SetCursorPos((x, y))
	# mouse_event is deprecated, sendInput is better but pywin32 doesn't have
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
	win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


# Move the cursor in screen based on X and Y coordinates. Very Fast.
# Library: pywin32 -> import win32api, time
def move_cursor(x, y, delay=None):
	win32api.SetCursorPos((x, y))
	if delay:
		time.sleep(delay)


# Get the current cursor info, like type and position.
# Library: pywin32 -> import win32gui
def get_cursor_info():
	cursor_info = win32gui.GetCursorInfo()
	print(cursor_info)
	return cursor_info


# Get pixel color on screen based on X and Y coordinates. Very Fast.
# Library: ctypes
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
	# NON RGB
	hdc = ctypes.windll.user32.GetDC(0)
	color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
	ctypes.windll.user32.ReleaseDC(0, hdc)
	return color


# Convert PIL images, sometimes we need to do it for better analysis
# Library: from PIL import Image, ImageFilter, cv2 as cv, numpy as np
def pil_image_convertions(pil_img):
	#https://hhsprings.bitbucket.io/docs/programming/examples/python/PIL/ImageFilter.html
	#https://hhsprings.bitbucket.io/docs/programming/examples/python/PIL/Image__class_Image.html#convert
	
	#converted_img = pil_img.convert('1')
	#converted_img = pil_img.convert('L')
	#converted_img = pil_img.convert('P')
	#converted_img = pil_img.convert('P', palette=Image.ADAPTIVE)
	#converted_img = pil_img.convert('1', dither=Image.NONE)
	#converted_img = pil_img.filter(filter=ImageFilter.BLUR)
	#converted_img = pil_img.filter(filter=ImageFilter.SMOOTH)
	#converted_img = pil_img.filter(filter=ImageFilter.CONTOUR)
	#converted_img = pil_img.filter(filter=ImageFilter.DETAIL)
	#converted_img = pil_img.filter(filter=ImageFilter.EDGE_ENHANCE)
	#converted_img = pil_img.filter(filter=ImageFilter.EDGE_ENHANCE_MORE)
	#converted_img = pil_img.filter(filter=ImageFilter.EMBOSS)
	#converted_img = pil_img.filter(filter=ImageFilter.FIND_EDGES)
	#converted_img = pil_img.filter(filter=ImageFilter.SHARPEN)
	#converted_img = pil_img.filter(filter=ImageFilter.SMOOTH)
	#converted_img = pil_img.filter(filter=ImageFilter.SMOOTH_MORE)
	#converted_img = pil_img.filter(filter=ImageFilter.GaussianBlur(radius=2))
	#converted_img = pil_img.filter(filter=ImageFilter.MaxFilter(size=3))
	#converted_img = pil_img.filter(filter=ImageFilter.MinFilter(size=3))
	#converted_img = pil_img.filter(filter=ImageFilter.MedianFilter(size=3))
	#converted_img = pil_img.getchannel(0)
	#converted_img = pil_img.getchannel(1)
	#converted_img = pil_img.getchannel(2)
	
	#converted_img.save('img_converted.png')

	#------------------------------------------------------------------#
	# Convertion from white text to black text - Very good for tesseract
	# https://stackoverflow.com/questions/57210342/improving-pytesseract-correct-text-recognition-from-image
	gray_pil_img = pil_img.convert('L') # Convert PIL img to gray
	cv_image = np.array(gray_pil_img) #  Convert PIL img to opencv img
	thresh = cv.threshold(cv_image, 225, 255, cv.THRESH_BINARY)[1] # Threshold to obtain binary image
	
	# remove noise / close gaps
	kernel =  np.ones((2, 2), np.uint8)
	close = cv.morphologyEx(thresh, cv.MORPH_CLOSE, kernel)

	# dilate result to make characters more solid
	kernel2 =  np.ones((2, 2), np.uint8)
	dilate = cv.dilate(close, kernel2, iterations = 1)
	
	converted_img = cv.bitwise_not(dilate) # Invert image
	cv.imwrite("img_converted.png", converted_img)
	#------------------------------------------------------------------#

	return converted_img


# Extract text from image using OCR
# Library: pytesseract.image_to_string, also need to install tesseract in computer and add to path.
def get_text_from_image(img):
	# get text and split in array
	text_list = image_to_string(img, lang='eng').split('\n')
	# Delete empty strings
	text_list = [i for i in text_list if i.strip()]
	#Print the list
	print(', '.join(text_list))
	return text_list


# Simple countdown
# Library: time
def start_countdown(sleep_time_sec=5):
	print('Starting', end='')
	for i in range(10):
		print('.', end='')
		time.sleep(sleep_time_sec/10)
	print('\nReady, forcing dwarves to work!')


# Print Figlet(Like a app title in terminal)
# Library: pyfiglet.Figlet
def print_logo(text_logo: str):
	figlet = Figlet(font='slant')
	print(figlet.renderText(text_logo))


# region Working with non active Windows

# Right Click on window based on X and Y coordinates. The window doesn't need to be active. Very Fast.
# Library: pywin32 -> import win32gui, time
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
	time.sleep(0.5)
	return hwnd[0]


# Right Click on window based on X and Y coordinates. The window doesn't need to be active. Very Fast.
# Library: pywin32 -> import win32api, pywin32 -> import win32con
# Need to use Microsoft Spy++(SpyXX) to simulate all messages depeding on the application
def right_click_window(hwnd, x, y):
	lParam = win32api.MAKELONG(x, y)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
	time.sleep(0.005)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)


# Save the mouse position, teleport the mouse, perform a click and then teleport the mouse to the original position
# Library: pywin32 -> import win32api, pywin32 -> import win32con
def magic_click(hwnd, x, y):
	old_pos = win32api.GetCursorPos()
	windll.user32.BlockInput(True)
	win32api.SetCursorPos((x, y))
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, 0)
	time.sleep(0.005)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, 0)
	time.sleep(0.015)
	win32api.SetCursorPos(old_pos)
	windll.user32.BlockInput(False)


# Wait for one click in screen to get the point(x, y) relative to window
# Library: from pynput.mouse import Listener as MouseListener, time
def get_window_point(hwnd):
	print("\nSelect the point. The first click will be considered.")
	pos = []
	x_win, y_win, cx_win, cy_win = win32gui.GetWindowRect(hwnd)

	def on_click(x, y, button, pressed):
		if pressed:
			pos.extend((x - x_win, y - y_win))
		if not pressed:
			return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	time.sleep(0.5)
	return pos


# Wait for two click in screen to get the region relative to window(x, y, width, height). use_coordinate to return (x, y, cx, cy).
# Library: from pynput.mouse import Listener as MouseListener, time
def get_window_region(hwnd, use_coordinates=False):
	print("\nSelect the top-left corner of area, then select the " +
		  "bottom-right corner.\nThe two first clicks will be considered.")

	region = []
	absolute_position = []
	is_first_click = [True]
	x_win, y_win, cx_win, cy_win = win32gui.GetWindowRect(hwnd)

	def on_click(x, y, button, pressed):
		if pressed:
			if is_first_click[0]:
				region.extend((x - x_win, y - y_win))
				absolute_position.extend((x, y))
				is_first_click[0] = False
			else:
				if not use_coordinates:
					width = x - absolute_position[0]
					height = y - absolute_position[1]
					region.extend((width, height))
				else:
					region.extend((x - x_win, y - y_win))
				return False

	with MouseListener(on_click=on_click) as mouse_listener:
		mouse_listener.join()

	time.sleep(0.5)
	return region


# Take screnshoot of a window even if it's in the background and save . Very fast.
# Library: pywin32 -> (win32gui, win32ui, win32con), PIL.Image
def window_screenshot(hwnd, region=None, save=False):
	# region: first fixel then width and height
	if not region:
		x, y, cx, cy = win32gui.GetWindowRect(hwnd)
		region = (0, 0, cx - x, cy - y)
	x, y, width, height = region

	wDC = win32gui.GetWindowDC(hwnd)
	dcObj = win32ui.CreateDCFromHandle(wDC)
	cDC = dcObj.CreateCompatibleDC()
	dataBitMap = win32ui.CreateBitmap()
	dataBitMap.CreateCompatibleBitmap(dcObj, width, height)
	cDC.SelectObject(dataBitMap)
	cDC.BitBlt((0, 0), (width, height), dcObj, (x, y), win32con.SRCCOPY)

	dataBitMap.SaveBitmapFile(cDC, 'screenshot.bmp')

	bmpinfo = dataBitMap.GetInfo()
	bmpstr = dataBitMap.GetBitmapBits(True)

	# PIL Image
	img = Image.frombuffer(
		'RGB',
		(bmpinfo['bmWidth'], bmpinfo['bmHeight']),
		bmpstr, 'raw', 'BGRX', 0, 1)

	# Numpy Image -> The fastest way to convert to OpenCV
	#img = np.fromstring(bmpstr, dtype='uint8')
	#img.shape = (height, width, 4)

	dcObj.DeleteDC()
	cDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, wDC)
	win32gui.DeleteObject(dataBitMap.GetHandle())

	if save:
		img.save('screenshot.png')
		#cv2.imwrite('screenshot.png', img)
	return img
# endregion


# Send a key down command to a window. Keys: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# Library: pywin32 -> (win32api, win32con)
def window_key_down(hwnd, key):
	win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, key, 0);


# Send a key up command to a window. Keys: https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes
# Library: pywin32 -> (win32api, win32con)
def window_key_up(hwnd, key):
	win32api.PostMessage(hwnd, win32con.WM_KEYUP, key, 0);
# endregion


def main():
	count = 0
	hwnd = win32gui.FindWindow(None, 'Clockworks Flyff - BalaNoAlvo')
	print('GetWindowText: ', win32gui.GetWindowText(hwnd))
	while 1:
		window_screenshot(hwnd)
		break
		""" 	
		region = get_window_region(hwnd)
		img = window_screenshot(hwnd, region, True)
		converted_img = image_convertion_test(img)
		print(get_text_from_image(converted_img))
		break
		"""
		""" 		
		if count > 500:
			window_key_down(hwnd, 0x44)
			time.sleep(0.01)
			window_key_up(hwnd, 0x44)
			break
		window_key_down(hwnd, 0x44)
		time.sleep(0.005)
		window_key_up(hwnd, 0x44)
		time.sleep(0.01)
		count += 1 
		"""


if __name__ == "__main__":
	main()
