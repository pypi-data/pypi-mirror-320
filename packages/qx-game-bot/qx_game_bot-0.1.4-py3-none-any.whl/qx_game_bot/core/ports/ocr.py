from abc import ABC, abstractmethod
from typing import Literal, TypeAlias
from pydantic import BaseModel

from qx_game_bot.core.domain.value_objects.img import Img

Point: TypeAlias = list[int, int]
Pos: TypeAlias = list[Point, Point, Point, Point]
TextCore: TypeAlias = tuple[str, float]
PosTextScore: TypeAlias = list[Pos, TextCore]


class Ocr(BaseModel, ABC):
    lang: str | Literal["ch", "en"] = "ch"

    @abstractmethod
    def ocr(self, img: str | Img, det_limit_side_len: int = 960) -> list[PosTextScore]:
        pass
