from time import sleep
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.screenshot import Screenshot
from qx_game_bot.core.ports.template_matcher import TemplateMatcher


class MatchScreenUsecase(BaseModel):
    templateMatcher: TemplateMatcher
    screenshot: Screenshot

    def execute(
        self,
        template: str | Img,
        minConfidence=0.9,
        retryCount=None,
        retryIntervalMS=200,
        monitor=None,
    ):
        def grabMatch():
            screenImg = self.screenshot.grab(monitor=monitor)
            res = self.templateMatcher.match(screenImg, template, minConfidence)
            return res

        res = grabMatch()

        if res is None and retryCount:
            for i in range(retryCount):
                sleep(retryIntervalMS / 1000)
                res = grabMatch()
                if res:
                    return res

        return res
