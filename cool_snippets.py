import pyautogui
import ctypes
from pathlib import Path

# Take Screenshot and save
im1 = pyautogui.screenshot(region=(650, 56, 20, 5)) #region, first fixel then width and height
im1.save(Path(__file__).parent/'life.png')


#get pixel color using ctypes, very fast, RGB or not.
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