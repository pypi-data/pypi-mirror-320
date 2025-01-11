import cv2
import numpy as np

from paddleocr import PaddleOCR

from e2e.utils.measure import measure

ocr = PaddleOCR(use_angle_cls=True)
imgPath = "e2e/ocr/image.png"


# Faster
def usePaddle(img=imgPath):
    result = ocr.ocr(img, cls=True)
    result = result[0]
    scores = [line[1][1] for line in result]
    print(f"Score Avg: {np.average(scores):.3f}")


# Slower, no need to use cv
def usePaddleBinary():
    img = cv2.imread(imgPath, 0)
    _, thresh = cv2.threshold(img, 117, 255, cv2.THRESH_BINARY)
    usePaddle(thresh)


measure(usePaddle, 5)
measure(usePaddleBinary, 5)
