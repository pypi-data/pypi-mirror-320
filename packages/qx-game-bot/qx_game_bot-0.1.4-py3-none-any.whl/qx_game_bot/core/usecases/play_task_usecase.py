from uuid import UUID
from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.ports.action_player import ActionPlayer
from pydantic import BaseModel

from qx_game_bot.core.ports.task_repository import TaskRepository


class PlayTaskUsecase(BaseModel):
    actionPlayer: ActionPlayer
    taskRepository: TaskRepository

    def execute(self, taskId: UUID = None, taskName: str = None):
        if taskId:
            task = self.taskRepository.getById(taskId)
        elif taskName:
            task = self.taskRepository.getByName(taskName)
        else:
            task = self.taskRepository.getAll()[-1]

        for action in task.actions:
            self.actionPlayer.play(action)
