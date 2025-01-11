from pathlib import Path
import cv2 as cv
import numpy as np

from e2e.utils.measure import Measure


img = cv.imread(Path(__file__).parent / "./example.png")


def showImg(winname, img, startPoint=None, endPoint=None):
    if startPoint and endPoint:
        img = cv.rectangle(img.copy(), startPoint, endPoint, (255, 0, 0), 2)
    cv.imshow(winname, img)


startPoint = None
endPoint = None
cropping = False
croppedImg = None


def handleMouse(event, x, y, flags, param):
    global startPoint, endPoint, cropping, croppedImg
    curPoint = (x, y)
    match event:
        case cv.EVENT_LBUTTONDOWN:
            if cropping:
                endPoint = curPoint
                cropping = False
                x1, y1 = startPoint
                x2, y2 = endPoint
                x1, x2 = min(x1, x2), max(x1, x2)
                y1, y2 = min(y1, y2), max(y1, y2)
                croppedImg = img[y1:y2, x1:x2]
                print((x1, y1))
            else:
                startPoint = curPoint
                endPoint = None
                cropping = True
        case cv.EVENT_MOUSEMOVE:
            if cropping:
                endPoint = curPoint
    showImg("Image", img, startPoint, endPoint)


cv.namedWindow("Image")
showImg("Image", img)
cv.setMouseCallback("Image", handleMouse)

cv.waitKey(0)
if croppedImg is not None:
    showImg("Cropped", croppedImg)
    cv.waitKey(0)

result = cv.matchTemplate(img, croppedImg, cv.TM_CCOEFF_NORMED)
loc = np.where(result >= 0.9)
for point in zip(*loc[::-1]):
    print(point)
minVal, maxVal, minLoc, maxLoc = cv.minMaxLoc(result)
h, w = croppedImg.shape[:2]
topLeftPoint = maxLoc
bottomRightPoint = (topLeftPoint[0] + w, topLeftPoint[1] + h)
matchedImg = img[
    topLeftPoint[1] : bottomRightPoint[1], topLeftPoint[0] : bottomRightPoint[0], :
]

showImg("Matched", matchedImg)
cv.waitKey(0)
print(maxVal)
print(maxLoc)
print(topLeftPoint, bottomRightPoint)
