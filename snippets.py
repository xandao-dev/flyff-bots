import pyautogui
import ctypes
import win32api
import win32con
import time
from pathlib import Path

# Take Screenshot (PIL Image) and save to a path
# Library: pyautogui, pathlib.Path
def take_screenshot(region=None):
	#region, first fixel then width and height
	if not region:
		region = (0, 0, pyautogui.size()[0], pyautogui.size()[1])
	scr = pyautogui.screenshot(region=region) 
	scr.save(Path(__file__).parent/'screenshot.png')


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


# Right Click on screen based on X and Y coordinates. Very Fast.
# Library: win32api, win32con
def right_click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

# Move the cursor in screen based on X and Y coordinates. Very Fast.
# Library: win32api, time
def move_cursor(x, y, delay=None):
	win32api.SetCursorPos((x, y))
	if delay:
		time.sleep(delay)


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
    else:
        pass  # Error occurred (invalid structure size?)


def main():
	take_screenshot()


if __name__ == "__main__":
	main()