from pydantic import BaseModel


class KeyPressAction(BaseModel):
    key: str
