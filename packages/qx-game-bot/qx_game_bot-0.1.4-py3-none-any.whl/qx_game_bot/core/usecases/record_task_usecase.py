from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.ports.keyboard_mouse_listener import KeyboardMouseListener
from qx_game_bot.core.ports.task_repository import TaskRepository
from pydantic import BaseModel


class RecordTaskUsecase(BaseModel):
    keyboardMouseActionListener: KeyboardMouseListener
    taskRepository: TaskRepository

    def execute(self, taskName: str | None = None):
        actions = []
        unsubscribe = self.keyboardMouseActionListener.onAction(handler=actions.append)

        def stop():
            unsubscribe()
            task = Task(actions=actions, taskName=taskName)
            self.taskRepository.save(task)
            return task

        return stop
