from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img


class ColorMatcher(BaseModel, ABC):
    @abstractmethod
    def match(
        self,
        img: str | Img,
        x: float,
        y: float,
        color: str | tuple[int, int, int],
        minConfidence: float = 0.99,
    ) -> bool:
        pass
