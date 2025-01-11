import time
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
from qx_game_bot.core.ports.action_player import ActionPlayer
import pynput


class PynputActionPlayer(ActionPlayer):
    def __init__(self):
        super().__init__()
        self._keyboardController = pynput.keyboard.Controller()
        self._mouseController = pynput.mouse.Controller()

    def _toKey(self, key: str):
        if len(key) > 1:
            return getattr(pynput.keyboard.Key, key)
        else:
            return key

    def _toButton(self, button: str):
        return getattr(pynput.mouse.Button, button)

    def play(self, action):
        match action:
            case DelayAction():
                time.sleep(action.timeoutMS / 1000)
            case KeyPressAction():
                self._keyboardController.press(self._toKey(action.key))
            case KeyReleaseAction():
                self._keyboardController.release(self._toKey(action.key))
            case KeyTapAction():
                self._keyboardController.tap(self._toKey(action.key))
            case KeyTypeAction():
                self._keyboardController.type(action.string)
            case MousePressAction():
                if action.x != None and action.y != None:
                    self._mouseController.position = (action.x, action.y)
                    time.sleep(0.05)
                self._mouseController.press(self._toButton(action.button))
            case MouseReleaseAction():
                if action.x != None and action.y != None:
                    self._mouseController.position = (action.x, action.y)
                    time.sleep(0.05)
                self._mouseController.release(self._toButton(action.button))
            case MouseTapAction():
                if action.x != None and action.y != None:
                    self._mouseController.position = (action.x, action.y)
                    time.sleep(0.05)
                self._mouseController.click(self._toButton(action.button))
            case MouseMoveAction():
                self._mouseController.position = (action.x, action.y)
            case MouseScrollAction():
                if action.x != None and action.y != None:
                    self._mouseController.position = (action.x, action.y)
                    time.sleep(0.05)
                self._mouseController.scroll(dx=action.dx, dy=action.dy)
