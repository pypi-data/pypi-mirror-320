from typing import Literal
from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.ocr import Ocr


class PaddleOcr(Ocr):
    def ocr(self, img, det_limit_side_len: int = 960):
        if not hasattr(self, "_ocr"):
            from paddleocr import PaddleOCR

            self._ocr = PaddleOCR(use_angle_cls=True, lang=self.lang)

        if det_limit_side_len:
            self._ocr.det_limit_side_len = det_limit_side_len

        if isinstance(img, Img):
            img = img.img

        result = self._ocr.ocr(img, cls=True)
        result = result[0]

        return result
