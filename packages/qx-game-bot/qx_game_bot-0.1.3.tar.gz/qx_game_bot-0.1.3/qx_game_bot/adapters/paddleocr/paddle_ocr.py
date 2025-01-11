from qx_game_bot.core.ports.ocr import Ocr


class PaddleOcr(Ocr):
    def ocr(self, img):
        if not hasattr(self, "_ocr"):
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(use_angle_cls=True)

        result = self._ocr.ocr(img, cls=True)
        result = result[0]

        return result
