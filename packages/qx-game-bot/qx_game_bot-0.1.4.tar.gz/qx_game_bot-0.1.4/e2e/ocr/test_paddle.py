import cv2
import numpy as np
from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang="ch")
imgPath = "e2e/ocr/image.png"
result = ocr.ocr(imgPath, cls=True)
result = result[0]

img = cv2.imread(imgPath)

for pos, (txt, score) in result:
    p1, p2, p3, p4 = np.array(pos).astype(int)
    cv2.rectangle(img, p1, p3, (0, 255, 0), 2)
    print(f"Text: {txt}, score: {score}\n")

cv2.imshow("Result", img)

cv2.waitKey(0)
