from pydantic import BaseModel


class KeyReleaseAction(BaseModel):
    key: str
