from typing import Literal
from pydantic import BaseModel


class MouseScrollAction(BaseModel):
    x: float | None = None
    y: float | None = None
    dx: float | None = None
    dy: float | None = None
