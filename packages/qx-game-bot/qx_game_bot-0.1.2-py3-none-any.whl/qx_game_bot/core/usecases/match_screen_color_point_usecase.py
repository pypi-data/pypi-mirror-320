from time import sleep
from typing import TypeAlias
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.color_matcher import ColorMatcher
from qx_game_bot.core.ports.screenshot import Screenshot
from qx_game_bot.core.ports.template_matcher import TemplateMatcher


class MatchScreenColorPointUsecase(BaseModel):
    colorMatcher: ColorMatcher
    screenshot: Screenshot

    def execute(
        self,
        color: str | tuple[int, int, int],
        x: int,
        y: int,
        minConfidence=0.9,
        retryCount=None,
        retryIntervalMS=200,
    ):
        def grabMatch():
            monitor = {"top": y, "left": x, "width": 1, "height": 1}
            screenImg = self.screenshot.grab(monitor=monitor)
            res = self.colorMatcher.match(
                screenImg,
                x=0,
                y=0,
                color=color,
                minConfidence=minConfidence,
            )
            return res

        res = grabMatch()

        if res is None and retryCount:
            for i in range(retryCount):
                sleep(retryIntervalMS / 1000)
                res = grabMatch()
                if res:
                    return res

        return res
