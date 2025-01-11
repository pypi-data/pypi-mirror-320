from abc import ABC, abstractmethod
from typing import Literal, TypeAlias
from pydantic import BaseModel

Point: TypeAlias = list[int, int]
Pos: TypeAlias = list[Point, Point, Point, Point]
TextCore: TypeAlias = tuple[str, float]
PosTextScore: TypeAlias = list[Pos, TextCore]


class Ocr(BaseModel, ABC):
    @abstractmethod
    def ocr(
        self,
        img: str | list,
    ) -> list[PosTextScore]:
        pass
