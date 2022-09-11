import cv2 as cv
import numpy as np
import win32con
import win32gui
import win32ui


class WindowCapture:

	# properties
	w = 0
	h = 0
	hwnd = None
	cropped_x = 0
	cropped_y = 0
	offset_x = 0
	offset_y = 0

	# constructor
	def __init__(self, hwnd):
		# find the handle for the window we want to capture
		self.hwnd = hwnd
		if not self.hwnd:
			raise Exception('Window not found')

		# get the window size
		window_rect = win32gui.GetWindowRect(self.hwnd)
		self.w = window_rect[2] - window_rect[0]
		self.h = window_rect[3] - window_rect[1]

		# account for the window border and titlebar and cut them off
		border_pixels = 8
		titlebar_pixels = 30
		self.w = self.w - (border_pixels * 2)
		self.h = self.h - titlebar_pixels - border_pixels
		self.cropped_x = border_pixels
		self.cropped_y = titlebar_pixels

		# set the cropped coordinates offset so we can translate screenshot
		# images into actual screen positions
		self.offset_x = window_rect[0] + self.cropped_x
		self.offset_y = window_rect[1] + self.cropped_y

	def get_screenshot(self):
		wDC = win32gui.GetWindowDC(self.hwnd)
		dcObj = win32ui.CreateDCFromHandle(wDC)
		cDC = dcObj.CreateCompatibleDC()
		dataBitMap = win32ui.CreateBitmap()
		dataBitMap.CreateCompatibleBitmap(dcObj, self.w, self.h)
		cDC.SelectObject(dataBitMap)
		cDC.BitBlt((0, 0), (self.w, self.h), dcObj,
				   (self.cropped_x, self.cropped_y), win32con.SRCCOPY)
		signedIntsArray = dataBitMap.GetBitmapBits(True)
		img = np.fromstring(signedIntsArray, dtype='uint8')
		img.shape = (self.h, self.w, 4)
		dcObj.DeleteDC()
		cDC.DeleteDC()
		win32gui.ReleaseDC(self.hwnd, wDC)
		win32gui.DeleteObject(dataBitMap.GetHandle())

		# drop the alpha channel, or cv.matchTemplate() will throw an error like:
		#   error: (-215:Assertion failed) (depth == CV_8U || depth == CV_32F) && type == _templ.type()
		#   && _img.dims() <= 2 in function 'cv::matchTemplate'
		img = img[..., :3]

		# make image C_CONTIGUOUS to avoid errors that look like:
		#   File ... in draw_rectangles
		#   TypeError: an integer is required (got type tuple)
		# see the discussion here:
		# https://github.com/opencv/opencv/issues/14866#issuecomment-580207109
		img = np.ascontiguousarray(img)

		# Convert image to gray
		img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

		return img

	# translate a pixel position on a screenshot image to a pixel position on the screen.
	# pos = (x, y)
	# WARNING: if you move the window being captured after execution is started, this will
	# return incorrect coordinates, because the window position is only calculated in
	# the __init__ constructor.
	def get_screen_position(self, pos):
		return (pos[0] + self.offset_x, pos[1] + self.offset_y)
