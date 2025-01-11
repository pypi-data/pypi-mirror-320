from abc import ABC
from typing import Any
from pydantic import BaseModel, Field


class MatchImgAction(BaseModel, ABC):
    img: str | Any = Field(exclude=True)
    minConfidence: float = None
    maxConfidence: float = None
    x1: int
    y1: int
    x2: int
    y2: int
