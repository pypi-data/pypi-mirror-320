import cv2
from mss import mss
import numpy as np


sct = mss()
imgArr = np.array(sct.grab(sct.monitors[1]))
imgArr = cv2.cvtColor(imgArr, cv2.COLOR_BGRA2BGR)


def colorToHSV(hexOrRgb: str | tuple[int, int, int]):
    hsv = None
    if isinstance(hexOrRgb, str):
        hex = hexOrRgb.lstrip("#")
        rgb = tuple(bytes.fromhex(hex))
        hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    elif isinstance(hexOrRgb, tuple):
        rgb = hexOrRgb
        hsv = cv2.cvtColor(np.uint8([[rgb]]), cv2.COLOR_RGB2HSV)[0][0]
    return hsv


def matchColorAtPoint(img, x, y, color, minConfidence=0.99):
    targetBGR = img[y, x]
    targetHSV = cv2.cvtColor(np.uint8([[targetBGR]]), cv2.COLOR_BGR2HSV)[0][0]
    colorHSV = colorToHSV(color)

    hTolerance = int(180 * (1 - minConfidence) * (1 + targetHSV[1] / 255))
    sTolerance = int(255 * (1 - minConfidence))
    vTolerance = int(255 * (1 - minConfidence))

    # 构建 HSV 颜色范围
    lowerHSV = np.array(
        [
            max(0, targetHSV[0] - hTolerance),
            max(0, targetHSV[1] - sTolerance),
            max(0, targetHSV[2] - vTolerance),
        ]
    )
    upperHSV = np.array(
        [
            min(180, targetHSV[0] + hTolerance),
            min(255, targetHSV[1] + sTolerance),
            min(255, targetHSV[2] + vTolerance),
        ]
    )

    # 使用 cv2.inRange 进行颜色判断(直接比较hsv值)
    mask = cv2.inRange(np.uint8([[colorHSV]]), lowerHSV, upperHSV)
    if mask[0][0] == 255:
        return True
    else:
        return False


print(matchColorAtPoint(imgArr, 400, 400, "4287f5"))
