from abc import ABC, abstractmethod
from uuid import UUID
from qx_game_bot.core.domain.task import Task
from pydantic import BaseModel


class TaskRepository(BaseModel, ABC):
    @abstractmethod
    def getById(self, id: UUID) -> Task:
        pass

    @abstractmethod
    def getByName(self, taskName: str) -> Task:
        pass

    @abstractmethod
    def getAll(self) -> list[Task]:
        pass

    @abstractmethod
    def save(self, task: Task):
        pass

    @abstractmethod
    def removeById(self, id: UUID):
        pass
