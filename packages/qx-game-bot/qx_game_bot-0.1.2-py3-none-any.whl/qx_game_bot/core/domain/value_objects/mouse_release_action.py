from typing import Literal
from pydantic import BaseModel


class MouseReleaseAction(BaseModel):
    button: Literal["left", "right", "middle"]
    x: int | None = None
    y: int | None = None
