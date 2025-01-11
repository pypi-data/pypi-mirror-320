from abc import ABC, abstractmethod

from pydantic import BaseModel

from qx_game_bot.core.domain.task import ActionType


class ActionPlayer(BaseModel, ABC):
    @abstractmethod
    def play(self, action: ActionType):
        pass
