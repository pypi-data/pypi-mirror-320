import cv2
import numpy as np
from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.color_matcher import ColorMatcher


class CvColorMatcher(ColorMatcher):
    def _colorToHSV(self, hexOrRgb: str | tuple[int, int, int]):
        hsv = None
        if isinstance(hexOrRgb, str):
            hex = hexOrRgb.lstrip("#")
            rgb = tuple(bytes.fromhex(hex))
            hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        elif isinstance(hexOrRgb, tuple):
            rgb = hexOrRgb
            hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
        return hsv

    def match(self, img, x, y, color, minConfidence=0.99):
        if isinstance(img, str):
            imgArr = cv2.imread(img)
            width = imgArr.shape[1]
            height = imgArr.shape[0]
            img = Img(img=imgArr, width=width, height=height)

        targetBGR = img.img[y, x]
        targetHSV = cv2.cvtColor(np.uint8([[targetBGR]]), cv2.COLOR_BGR2HSV)[0][0]
        colorHSV = self._colorToHSV(color)

        hTolerance = int(180 * (1 - minConfidence) * (1 + targetHSV[1] / 255))
        sTolerance = int(255 * (1 - minConfidence))
        vTolerance = int(255 * (1 - minConfidence))

        # 构建 HSV 颜色范围
        lowerHSV = np.array(
            [
                max(0, int(targetHSV[0]) - hTolerance),
                max(0, int(targetHSV[1]) - sTolerance),
                max(0, int(targetHSV[2]) - vTolerance),
            ]
        )
        upperHSV = np.array(
            [
                min(180, int(targetHSV[0]) + hTolerance),
                min(255, int(targetHSV[1]) + sTolerance),
                min(255, int(targetHSV[2]) + vTolerance),
            ]
        )

        # 使用 cv2.inRange 进行颜色判断(直接比较hsv值)
        mask = cv2.inRange(np.uint8([[colorHSV]]), lowerHSV, upperHSV)
        if mask[0][0] == 255:
            return True
        else:
            return False
