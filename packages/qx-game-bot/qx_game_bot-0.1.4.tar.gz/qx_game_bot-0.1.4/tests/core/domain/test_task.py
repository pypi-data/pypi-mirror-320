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
import pytest


@pytest.fixture
def actions():
    return [
        DelayAction(timeoutMS=100),
        DelayAction.fromSeconds(sec=1),
        KeyPressAction(key="d"),
        KeyReleaseAction(key="d"),
        KeyTapAction(key="d"),
        MousePressAction(button="left"),
        MouseReleaseAction(button="left"),
        MouseTapAction(button="left"),
        MouseMoveAction(x=100, y=100),
        MouseScrollAction(x=100, y=100, dx=100, dy=0),
    ]


def test_actions_creation(actions):
    pass


def test_task():
    task = Task(taskName="task1")
    assert task.taskName == "task1"

    task.rename("mytask")
    assert task.taskName == "mytask"

    task.addAction(DelayAction(timeoutMS=1000))
    assert isinstance(task.actions[0], DelayAction)

    task.removeAction(0)
    assert task.actions == []
