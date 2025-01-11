from pathlib import Path
from timeit import repeat
import cv2
from numpy import average

from e2e.utils.measure import measure


def resize(img, ratio=0.25):
    h, w = img.shape[:2]
    newH, newW = (int(h * ratio), int(w * ratio))
    return cv2.resize(img, (newW, newH))


def imshowWaitkey(winname, img):
    cv2.imshow(winname, img)
    cv2.waitKey(0)


#     return nextLoc
def pyramidMatchTemplate(img, template, level=3, buffer=12, debug=False):
    imgs = [img]
    temps = [template]
    buffers = [buffer]
    for i in range(level - 1):
        imgs.insert(0, cv2.pyrDown(imgs[0]))
        temps.insert(0, cv2.pyrDown(temps[0]))
        buffers.insert(0, int(buffers[0] / 2))

    prevVal = None
    prevLoc = None
    for i in range(level):
        curImg = imgs[i]
        curTemp = temps[i]
        curBuffer = buffers[i]

        if debug:
            imshowWaitkey("curImg", curImg)
            imshowWaitkey("curTemp", curTemp)

        if prevLoc is None:
            res = cv2.matchTemplate(curImg, curTemp, cv2.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
            prevLoc = maxLoc
        else:
            x, y = prevLoc
            x = x * 2 - curBuffer
            y = y * 2 - curBuffer
            h, w = curTemp.shape[:2]
            h += curBuffer
            w += curBuffer
            roi = curImg[y : y + h, x : x + w]
            res = cv2.matchTemplate(roi, curTemp, cv2.TM_CCOEFF_NORMED)
            minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(res)
            prevVal = maxVal
            prevLoc = maxLoc[0] + x, maxLoc[1] + y

    return prevVal, prevLoc


img = cv2.imread(Path(__file__).parent / "./example.png")
croppedImg = img[100:300, 500:600]

grayImg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
grayCroppedImg = cv2.cvtColor(croppedImg, cv2.COLOR_BGR2GRAY)

resizedImg = resize(img)
resizedCroppedImg = resize(croppedImg)

resizedGrayImg = resize(grayImg)
resizedGrayCroppedImg = resize(grayCroppedImg)

blurImg = cv2.GaussianBlur(img, (5, 5), 0)
blurCroppedImg = cv2.GaussianBlur(croppedImg, (5, 5), 0)

# smallImg = cv2.pyrDown(img)
# cv2.imshow("small img", smallImg)
# cv2.imshow("resized img", resizedImg)
# cv2.waitKey(0)


def normalMatch():
    result = cv2.matchTemplate(img, croppedImg, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    print(f"Confidence: {maxVal:.2f}, left top point: {maxLoc}")


def grayMatch():
    result = cv2.matchTemplate(grayImg, grayCroppedImg, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    print(f"Confidence: {maxVal:.2f}, left top point: {maxLoc}")


def normalResizedMatch():
    result = cv2.matchTemplate(resizedImg, resizedCroppedImg, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    print(f"Confidence: {maxVal:.2f}, left top point: {maxLoc}")


def normalResizedGrayMatch():
    result = cv2.matchTemplate(
        resizedGrayImg, resizedGrayCroppedImg, cv2.TM_CCOEFF_NORMED
    )
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    print(f"Confidence: {maxVal:.2f}, left top point: {maxLoc}")


def pyramidMatch():
    val, loc = pyramidMatchTemplate(img, croppedImg, level=4)
    print(f"Confidence: {val:.2f}, left top point: {loc}")


def pyramidMatchDebug():
    val, loc = pyramidMatchTemplate(img, croppedImg, level=4, debug=True)
    print(f"Confidence: {val:.2f}, left top point: {loc}")


def pyramidGrayMatch():
    val, loc = pyramidMatchTemplate(grayImg, grayCroppedImg, level=3)
    print(f"Confidence: {val:.2f}, left top point: {loc}")


def blurredMatch():
    result = cv2.matchTemplate(blurImg, blurCroppedImg, cv2.TM_CCOEFF_NORMED)
    (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(result)
    print(f"Confidence: {maxVal:.2f}, left top point: {maxLoc}")


# measure(normalMatch, 100)
# measure(grayMatch, 100)
# measure(normalResizedMatch, 100)
# measure(normalResizedGrayMatch, 100)
# measure(pyramidMatch, 100)
# measure(pyramidGrayMatch, 100)
measure(blurredMatch, 100)
