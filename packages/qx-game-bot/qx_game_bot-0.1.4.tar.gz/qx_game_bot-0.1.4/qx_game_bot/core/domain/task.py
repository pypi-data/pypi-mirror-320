from datetime import datetime
from typing import Union
from uuid import UUID, uuid4
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.domain.value_objects.key_press_action import KeyPressAction
from qx_game_bot.core.domain.value_objects.key_release_action import (
    KeyReleaseAction,
)
from qx_game_bot.core.domain.value_objects.key_tap_action import KeyTapAction
from qx_game_bot.core.domain.value_objects.key_type_action import KeyTypeAction
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
from pydantic import BaseModel, Field

ActionType = Union[
    DelayAction,
    KeyPressAction,
    KeyReleaseAction,
    KeyTapAction,
    KeyTypeAction,
    MousePressAction,
    MouseReleaseAction,
    MouseTapAction,
    MouseMoveAction,
    MouseScrollAction,
]


class Task(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    createdAt: datetime = Field(default_factory=datetime.now)
    taskName: str = ""
    actions: list[ActionType] = Field(default_factory=list)

    def rename(self, newname):
        self.taskName = newname

    def addAction(self, action: ActionType):
        self.actions.append(action)

    def removeAction(self, index):
        del self.actions[index]
