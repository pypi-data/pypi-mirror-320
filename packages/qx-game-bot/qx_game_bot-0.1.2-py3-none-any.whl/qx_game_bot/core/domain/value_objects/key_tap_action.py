from pydantic import BaseModel


class KeyTapAction(BaseModel):
    key: str
