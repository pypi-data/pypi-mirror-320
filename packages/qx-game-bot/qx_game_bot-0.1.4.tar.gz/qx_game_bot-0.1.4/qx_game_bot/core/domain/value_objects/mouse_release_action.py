from typing import Literal
from pydantic import BaseModel


class MouseReleaseAction(BaseModel):
    button: Literal["left", "right", "middle"]
    x: float | None = None
    y: float | None = None
