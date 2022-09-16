from time import sleep, time
from pathlib import Path
import cv2 as cv
import numpy as np

inventory_trash_path = str(Path(__file__).parent / 'test_assets' /  'inventory_trash.png')
frame_inventory_open_path = str(Path(__file__).parent / 'test_assets' /  'frame_inventory_open.png')
INVENTORY_TRASH = cv.imread(inventory_trash_path, cv.IMREAD_GRAYSCALE)
FRAME_INVENTORY_OPEN = cv.imread(frame_inventory_open_path, cv.IMREAD_GRAYSCALE)


def check_if_inventory_is_open(threshold):
        needle_w = INVENTORY_TRASH.shape[0]
        needle_h = INVENTORY_TRASH.shape[1]

        # There are 6 methods to choose from:
        # TM_CCOEFF, TM_CCOEFF_NORMED, TM_CCORR, TM_CCORR_NORMED, TM_SQDIFF, TM_SQDIFF_NORMED
        method = cv.TM_CCOEFF_NORMED
        # Mask as the needle, to remove the black pixels
        result = cv.matchTemplate(FRAME_INVENTORY_OPEN, INVENTORY_TRASH, method, mask=INVENTORY_TRASH)

        # Get the best match position from the match result.
        min_val, max_val, min_loc, max_loc = cv.minMaxLoc(result)

        print(min_val, max_val)
        if max_val < threshold:
            print("Inventory is not open")
            return False

        line_color = (0, 255, 0)
        line_type = cv.LINE_4
        top_left = (max_loc[0], max_loc[1])
        bottom_right = (max_loc[0] + needle_w, max_loc[1] + needle_h)
        cv.rectangle(FRAME_INVENTORY_OPEN, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)

        top_left = (min_loc[0], min_loc[1])
        bottom_right = (min_loc[0] + needle_w, min_loc[1] + needle_h)
        cv.rectangle(FRAME_INVENTORY_OPEN, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)

        cv.imshow('Matches', FRAME_INVENTORY_OPEN)
        cv.waitKey(0)

def main():
    check_if_inventory_is_open(0.6)

if __name__ == "__main__":
	main()
