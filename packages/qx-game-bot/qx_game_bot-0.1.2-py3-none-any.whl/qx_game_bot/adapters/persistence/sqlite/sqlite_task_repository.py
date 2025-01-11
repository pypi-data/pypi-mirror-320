import json
from qx_game_bot.adapters.persistence.sqlite.db import database
from qx_game_bot.adapters.persistence.sqlite.models.task_model import TaskModel
from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.domain.value_objects.key_press_action import KeyPressAction
from qx_game_bot.core.domain.value_objects.key_release_action import (
    KeyReleaseAction,
)
from qx_game_bot.core.domain.value_objects.key_tap_action import KeyTapAction
from qx_game_bot.core.domain.value_objects.mouse_move_action import MouseMoveAction
from qx_game_bot.core.domain.value_objects.mouse_press_action import (
    MousePressAction,
)
from qx_game_bot.core.domain.value_objects.mouse_release_action import (
    MouseReleaseAction,
)
from qx_game_bot.core.domain.value_objects.mouse_scroll_action import (
    MouseScrollAction,
)
from qx_game_bot.core.domain.value_objects.mouse_tap_action import MouseTapAction
from qx_game_bot.core.ports.task_repository import TaskRepository


class SqliteTaskRepository(TaskRepository):
    def __init__(self):
        database.create_tables([TaskModel])

    def getById(self, id):
        model = TaskModel.get_by_id(id)
        task = self._toDomain(model)
        return task

    def getByName(self, taskName):
        model = TaskModel.get(taskName=taskName)
        task = self._toDomain(model)
        return task

    def getAll(self):
        models = TaskModel.select()
        tasks = [self._toDomain(model) for model in models]
        return tasks

    def save(self, task):
        actions = []

        for action in task.actions:
            a = action.model_dump()
            a["name"] = action.__class__.__name__
            actions.append(a)

        TaskModel.get_or_create(
            id=task.id,
            createdAt=task.createdAt,
            taskName=task.taskName,
            actions=json.dumps(actions),
        )

    def removeById(self, id):
        TaskModel.delete_by_id(id)

    def _toDomain(self, taskModel: TaskModel):
        actions = []
        for actionDict in json.loads(taskModel.actions):
            match actionDict["name"]:
                case DelayAction.__name__:
                    action = DelayAction(**actionDict)
                case KeyPressAction.__name__:
                    action = KeyPressAction(**actionDict)
                case KeyReleaseAction.__name__:
                    action = KeyReleaseAction(**actionDict)
                case KeyTapAction.__name__:
                    action = KeyTapAction(**actionDict)
                case MousePressAction.__name__:
                    action = MousePressAction(**actionDict)
                case MouseReleaseAction.__name__:
                    action = MouseReleaseAction(**actionDict)
                case MouseTapAction.__name__:
                    action = MouseTapAction(**actionDict)
                case MouseMoveAction.__name__:
                    action = MouseMoveAction(**actionDict)
                case MouseScrollAction.__name__:
                    action = MouseScrollAction(**actionDict)
                case _:
                    continue
            actions.append(action)

        return Task(
            id=taskModel.id,
            createdAt=taskModel.createdAt,
            taskName=taskModel.taskName,
            actions=actions,
        )
