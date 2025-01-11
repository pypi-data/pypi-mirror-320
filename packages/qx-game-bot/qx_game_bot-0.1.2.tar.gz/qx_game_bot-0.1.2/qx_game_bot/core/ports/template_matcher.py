from abc import ABC, abstractmethod
from typing import TypeAlias

from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img

Point: TypeAlias = tuple[int, int]


class TemplateMatcher(BaseModel, ABC):
    @abstractmethod
    def match(
        self,
        img: str | Img,
        template: str | Img,
        minConfidence: float = 0.9,
    ) -> Point | None:
        pass

    @abstractmethod
    def matchAll(
        self,
        img: str | Img,
        template: str | Img,
        minConfidence: float = 0.9,
    ) -> list[Point] | None:
        pass
