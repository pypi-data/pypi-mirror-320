import cv2
import numpy as np
from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.template_matcher import TemplateMatcher


class CvTemplateMatcher(TemplateMatcher):
    debug: bool | None = None

    def _getMidPoint(self, imgArr, x, y):
        h, w = imgArr.shape[:2]
        centerX = int(x + int(w / 2))
        centerY = int(y + int(h / 2))
        return (centerX, centerY)

    def match(self, img, template, minConfidence=0.9):
        if isinstance(img, str):
            imgArr = cv2.imread(img)
            width = imgArr.shape[1]
            height = imgArr.shape[0]
            img = Img(img=imgArr, width=width, height=height)
        if isinstance(template, str):
            tempArr = cv2.imread(template)
            width = tempArr.shape[1]
            height = tempArr.shape[0]
            template = Img(img=tempArr, width=width, height=height)

        res = cv2.matchTemplate(img.img, template.img, cv2.TM_CCOEFF_NORMED)
        minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)

        if maxVal < minConfidence:
            return None

        if self.debug:
            cv2.imshow("Match", template.img)
            cv2.waitKey(1)

        point = self._getMidPoint(template.img, *maxLoc)
        return point

    def matchAll(self, img, template, minConfidence=0.9):
        if isinstance(img, str):
            imgArr = cv2.imread(img)
            width = imgArr.shape[1]
            height = imgArr.shape[0]
            img = Img(img=imgArr, width=width, height=height)
        if isinstance(template, str):
            tempArr = cv2.imread(template)
            width = tempArr.shape[1]
            height = tempArr.shape[0]
            template = Img(img=tempArr, width=width, height=height)

        res = cv2.matchTemplate(img.img, template.img, cv2.TM_CCOEFF_NORMED)
        locations = np.where(res >= minConfidence)
        locations = list(zip(*locations[::-1]))

        rectangles = []
        tempH, tempW = template.img.shape[:2]
        for loc in locations:
            rect = [int(loc[0]), int(loc[1]), tempW, tempH]
            rectangles.append(rect)
            rectangles.append(rect)
        rectangles, weights = cv2.groupRectangles(rectangles, groupThreshold=1, eps=0.5)

        if not len(rectangles):
            return None

        points = []
        for x, y, w, h in rectangles:
            points.append(self._getMidPoint(template.img, x, y))

        return points
