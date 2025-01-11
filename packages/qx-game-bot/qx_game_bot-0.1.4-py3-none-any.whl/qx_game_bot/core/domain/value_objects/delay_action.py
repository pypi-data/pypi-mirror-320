import time
from pydantic import BaseModel, ConfigDict


class DelayAction(BaseModel):
    timeoutMS: float

    @staticmethod
    def fromSeconds(sec: float):
        return DelayAction(timeoutMS=sec * 1000)
