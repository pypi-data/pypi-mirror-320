from time import sleep
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.screenshot import Screenshot
from qx_game_bot.core.ports.template_matcher import TemplateMatcher


class MatchAllTemplatesUsecase(BaseModel):
    templateMatcher: TemplateMatcher

    def execute(
        self,
        img: str | Img,
        template: str | Img,
        minConfidence=0.9,
        retryCount=None,
        retryIntervalMS=200,
    ):
        res = self.templateMatcher.matchAll(img, template, minConfidence)

        if res is None and retryCount:
            for i in range(retryCount):
                if retryIntervalMS:
                    sleep(retryIntervalMS / 1000)
                res = self.templateMatcher.matchAll(img, template, minConfidence)
                if res:
                    break

        return res
