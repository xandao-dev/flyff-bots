import pyautogui
import ctypes
import time
from pyfiglet import Figlet
from pytesseract import image_to_string
from pathlib import Path

# install pywin32 to use these modules and execute the installer in Scripts folder
# https://github.com/mhammond/pywin32
import win32api # subpackage of pywin32
import win32con # subpackage of pywin32
import win32gui # subpackage of pywin32
import win32ui  # subpackage of pywin32

# Take Screenshot (PIL Image) and save to a path. pyautogui is very slow.
# Library: pyautogui, pathlib.Path
def take_screenshot(region=None):
	#region, first fixel then width and height
	if not region:
		region = (0, 0, pyautogui.size()[0], pyautogui.size()[1])
	scr = pyautogui.screenshot(region=region) 
	scr.save(Path(__file__).parent/'screenshot.png')


# Right Click on screen based on X and Y coordinates. Very Fast.
# Library: pywin32 -> import win32api, pywin32 -> import win32con
def right_click(x, y):
    win32api.SetCursorPos((x, y))
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


# Get the current cursor type, like arrow, pointer, etc. Very Fast.
# Library: ctypes
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
        return info.hCursor		
    else:
        return  # Error occurred (invalid structure size?)


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
	#NON RGB
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    return color


# Extract text from image using OCR
# Library: pytesseract.image_to_string, also need to install tesseract in computer and add to path.
def get_text_from_image(pil_img):
	#get text and split in array
	text_list = image_to_string(pil_img, lang='eng').split('\n')
	#Delete empty strings
	text_list = [i for i in text_list if i.strip()]
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


#region Working with non active Windows

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
def right_click_window(hwnd, x, y):
	lParam = win32api.MAKELONG(x, y)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lParam)
	win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, None, lParam)

#endregion

def main():
	while 1:
		print('FindWindow:', win32gui.FindWindow(None, 'Clockworks Flyff - xandao6'))
		print('GetForegroundWindow:', win32gui.GetForegroundWindow())

		print('GetWindowText: ', win32gui.GetWindowText(win32gui.FindWindow(None, 'Clockworks Flyff - xandao6')))
		time.sleep(0.25)


if __name__ == "__main__":
	main()