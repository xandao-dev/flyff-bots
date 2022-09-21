import cv2 as cv
import numpy as np

MATCH_METHODS = {
    "TM_CCOEFF": cv.TM_CCOEFF,
    "TM_CCOEFF_NORMED": cv.TM_CCOEFF_NORMED,
    "TM_CCORR": cv.TM_CCORR,
    "TM_CCORR_NORMED": cv.TM_CCORR_NORMED,
    "TM_SQDIFF": cv.TM_SQDIFF,
    "TM_SQDIFF_NORMED": cv.TM_SQDIFF_NORMED,
}


class ComputerVision:
    def __init__(self) -> None:
        pass

    @staticmethod
    def match_template(frame, template, method=MATCH_METHODS["TM_CCOEFF_NORMED"], threshold=0.7, draw=True):
        """
        Match template in a frame.

        :param frame: Frame to search in.
        :param template: Template to search for.
        :param method: Method to use for matching. Default is TM_CCOEFF_NORMED.
        :param threshold: Threshold to use for matching. Default is 0.7.
        :param draw: Draw rectangle around the match. Default: True.

        :return: max_val, max_loc, center_loc, pass_threshold, frame
        """
        template_h = template.shape[0]
        template_w = template.shape[1]
        result = cv.matchTemplate(frame, template, method)
        _, max_val, _, max_loc = cv.minMaxLoc(result)
        center_loc = (max_loc[0] + template_w // 2, max_loc[1] + template_h // 2)
        pass_threshold = max_val >= threshold

        # Draw a rectangle around the match, that's why we return the frame
        if draw:
            line_color = (0, 255, 0)
            line_type = cv.LINE_4
            top_left = max_loc
            bottom_right = (top_left[0] + template_w, top_left[1] + template_h)
            cv.rectangle(frame, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)

        return max_val, max_loc, center_loc, pass_threshold, frame

    @staticmethod
    def match_template_multi(frame, template, method=MATCH_METHODS["TM_CCOEFF_NORMED"], threshold=0.7, box_offset=(0, 0), draw_rect=True, draw_marker=False):
        """
        Match template, multiple times, in image. Return only the matches that pass the threshold.

        :param frame: Frame to search in.
        :param template: Template to search for.
        :param method: Method to use for matching. Default is TM_CCOEFF_NORMED.
        :param threshold: Threshold to use for matching. Default is 0.7.
        :param box_offset: Increase the box size by this offset. Default is (0, 0) for (width, height).
        :param draw_rect: Draw rectangle around the match. Default: True.
        :param draw_marker: Draw marker at the center of the match. Default: False.

        :return: matches, frame
        """
        template_h = template.shape[0]
        template_w = template.shape[1]
        result = cv.matchTemplate(frame, template, method)

        # Get the all the positions from the match result that exceed our threshold
        locations = np.where(result >= threshold)
        # From [[y1, y2, y3], [x1, x2, x3]] to [(x1, y1), (x2, y2), (x3, y3)]
        locations = list(zip(*locations[::-1]))
        # print(locations)

        # Create a list of [x, y, w, h] rectangles
        rectangles = []
        for loc in locations:
            rect = [loc[0], loc[1], template_w + box_offset[0], template_h + box_offset[1]]
            # Add every box to the list twice in order to retain single (non-overlapping) boxes
            rectangles.append(rect)
            rectangles.append(rect)

        # Overlapping rectangles get drawn. We can eliminate those redundant locations by using groupRectangles().
        # The groupThreshold parameter should usually be 1. If you put it at 0 then no grouping is done.
        # If you put it at 2 then an object needs at least 3 overlapping rectangles to appear
        # eps 0.5 means: "Relative difference between sides of the rectangles to merge them into a group."
        rectangles, weights = cv.groupRectangles(rectangles, groupThreshold=1, eps=0.5)
        # print(rectangles)

        matches = []
        if len(rectangles):
            # print('Found template')
            for (x, y, w, h) in rectangles:
                # Determine the center position
                center_x = x + w // 2
                center_y = y + h // 2
                # Save the matches
                matches.append((center_x, center_y))

                if draw_rect:
                    line_color = (0, 255, 0)
                    line_type = cv.LINE_4
                    top_left = (x, y)
                    bottom_right = (x + w, y + h)
                    cv.rectangle(frame, top_left, bottom_right, color=line_color, lineType=line_type, thickness=2)
                if draw_marker:
                    marker_color = (255, 0, 255)
                    marker_type = cv.MARKER_CROSS
                    cv.drawMarker(
                        frame,
                        (center_x, center_y),
                        color=marker_color,
                        markerType=marker_type,
                        markerSize=40,
                        thickness=2,
                    )
                    # cv.putText(frame, f'({center_x}, {center_y})', (x+w, y+h),
                    # cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        return matches, frame