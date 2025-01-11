from pydantic import BaseModel

from qx_game_bot.core.ports.ocr import Ocr
from qx_game_bot.core.ports.screenshot import Screenshot


class ScreenOcrUsecase(BaseModel):
    ocr: Ocr
    screenshot: Screenshot

    def execute(
        self,
        returnPosAndScores: bool = False,
        minConfidence=None,
        monitor=None,
    ):
        screenImg = self.screenshot.grab(monitor=monitor)

        img = screenImg.img

        res = self.ocr.ocr(img)

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
