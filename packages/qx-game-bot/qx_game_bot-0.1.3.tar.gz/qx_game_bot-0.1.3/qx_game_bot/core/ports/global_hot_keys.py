from abc import ABC, abstractmethod
from typing import Callable, TypeAlias
from pydantic import BaseModel

# Unsubscribe: TypeAlias = Callable


class GlobalHotKeys(BaseModel, ABC):
    @abstractmethod
    def bind(self, config: dict[str, Callable]):
        pass
