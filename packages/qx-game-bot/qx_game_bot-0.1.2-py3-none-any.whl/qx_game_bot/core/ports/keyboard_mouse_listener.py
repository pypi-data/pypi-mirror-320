from abc import ABC, abstractmethod
from typing import Callable, TypeAlias

from pydantic import BaseModel

from qx_game_bot.core.domain.task import ActionType

Unsubscribe: TypeAlias = Callable


class KeyboardMouseListener(BaseModel, ABC):
    @abstractmethod
    def onAction(self, handler: Callable[[ActionType], None]) -> Unsubscribe:
        pass
