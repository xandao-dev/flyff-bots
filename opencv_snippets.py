from time import time
from PIL import Image
import collections
import win32gui, win32con, win32ui
import numpy as np
import cv2


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

	bmpstr = dataBitMap.GetBitmapBits(True)
	img = np.fromstring(bmpstr, dtype='uint8')
	img.shape = (height, width, 4)
	
	dcObj.DeleteDC()
	cDC.DeleteDC()
	win32gui.ReleaseDC(hwnd, wDC)
	win32gui.DeleteObject(dataBitMap.GetHandle())

	if save:
		cv2.imwrite('screenshot.png', img)
	return img


def main():
	hwnd = win32gui.FindWindow(None, 'Clockworks Flyff - BalaNoAlvo')

	loop_time = time()
	fps = collections.deque(maxlen=60)
	while True:
		screenshot = window_screenshot(hwnd, save=True)

		cv2.imshow('Computer Vision', screenshot)
		fps.append(1 / (time() - loop_time))
		print(f'FPS Average: {round(sum(fps)/fps.maxlen)} fps')
		loop_time = time()

		if cv2.waitKey(1) == ord('q'):
			cv2.destroyAllWindows()
			break


if __name__ == '__main__':
	main()