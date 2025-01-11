from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.ocr import Ocr
from qx_game_bot.core.ports.screenshot import Screenshot


class ImgOcrUsecase(BaseModel):
    ocr: Ocr

    def execute(
        self,
        img: str | Img,
        returnPosAndScores: bool = False,
        minConfidence=None,
        det_limit_side_len: int = 960,
    ):

        res = self.ocr.ocr(img, det_limit_side_len=det_limit_side_len)

        returnList = []

        for pos, (text, score) in res:
            if minConfidence and score < minConfidence:
                continue

            if returnPosAndScores:
                item = [pos, text, score]
                returnList.append(item)
            else:
                returnList.append(text)

        return returnList
