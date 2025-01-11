from typing import Literal
from pydantic import BaseModel


class MouseMoveAction(BaseModel):
    x: int
    y: int
