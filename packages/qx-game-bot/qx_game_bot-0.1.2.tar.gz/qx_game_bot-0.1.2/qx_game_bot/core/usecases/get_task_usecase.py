from uuid import UUID
from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.ports.action_player import ActionPlayer
from pydantic import BaseModel

from qx_game_bot.core.ports.task_repository import TaskRepository


class GetTaskUsecase(BaseModel):
    taskRepository: TaskRepository

    def execute(
        self,
        taskId: UUID = None,
        taskName: str | None = None,
        getLastOne=False,
        getAll=False,
    ):
        if taskId:
            task = self.taskRepository.getById(taskId)
            return task
        elif taskName:
            task = self.taskRepository.getByName(taskName)
            return task
        elif getLastOne is True:
            task = self.taskRepository.getAll()[-1]
            return task
        elif getAll is True:
            tasks = self.taskRepository.getAll()
            return tasks
