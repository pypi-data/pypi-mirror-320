from typing import Literal
from pydantic import BaseModel


class MouseScrollAction(BaseModel):
    x: int | None = None
    y: int | None = None
    dx: int | None = None
    dy: int | None = None
