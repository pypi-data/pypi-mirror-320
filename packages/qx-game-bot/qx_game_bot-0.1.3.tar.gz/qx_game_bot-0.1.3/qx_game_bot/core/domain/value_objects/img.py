from abc import ABC
from typing import Any
from pydantic import BaseModel, Field


class Img(BaseModel, ABC):
    img: str | Any = Field(exclude=True)
    width: int
    height: int
