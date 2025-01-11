from abc import ABC, abstractmethod
from typing import TypedDict
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img


class MonitorRegion(TypedDict):
    top: int
    left: int
    width: int
    height: int


class Screenshot(BaseModel, ABC):
    @abstractmethod
    def grab(self, monitor: MonitorRegion | int | None = None) -> Img:
        pass
