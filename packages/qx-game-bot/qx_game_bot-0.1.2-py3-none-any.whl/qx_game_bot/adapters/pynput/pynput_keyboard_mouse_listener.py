from time import time
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.domain.value_objects.key_press_action import KeyPressAction
from qx_game_bot.core.domain.value_objects.key_release_action import (
    KeyReleaseAction,
)
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
from qx_game_bot.core.ports.keyboard_mouse_listener import KeyboardMouseListener
from pynput import keyboard, mouse


class PynputKeyboardMouseListener(KeyboardMouseListener):
    _listeners: list
    _lasttime: time

    def model_post_init(self, __contexts):
        self._listeners = []

    def _emit(self, action):
        now = time()
        timeoutSec = now - self._lasttime
        delayAction = DelayAction.fromSeconds(timeoutSec)
        self._lasttime = now

        for listener in self._listeners:
            listener(delayAction)
            listener(action)

    def _handlePress(self, key: keyboard.Key | keyboard.KeyCode | None):
        try:
            action = KeyPressAction(key=str(key.char))
        except:
            action = KeyReleaseAction(key=str(key).split("Key.")[1])
        self._emit(action)

    def _handleRelease(self, key: keyboard.Key | keyboard.KeyCode | None):
        try:
            action = KeyReleaseAction(key=str(key.char))
        except:
            action = KeyReleaseAction(key=str(key).split("Key.")[1])
        self._emit(action)

    def _handleClick(self, x, y, button, pressed):
        if button == mouse.Button.left:
            buttonStr = "left"
        elif button == mouse.Button.middle:
            buttonStr = "middle"
        elif button == mouse.Button.right:
            buttonStr = "right"

        if pressed:
            self._emit(MousePressAction(x=x, y=y, button=buttonStr))
        else:
            self._emit(MouseReleaseAction(x=x, y=y, button=buttonStr))

    def _handleMove(self, x, y):
        self._emit(MouseMoveAction(x=x, y=y))

    def _handleScroll(self, x, y, dx, dy):
        self._emit(MouseScrollAction(x=x, y=y, dx=dx, dy=dy))

    def onAction(self, handler):
        self._listeners.append(handler)
        self._lasttime = time()

        if hasattr(self, "_kl"):
            return

        self._kl = keyboard.Listener(
            on_press=self._handlePress, on_release=self._handleRelease
        )
        self._ml = mouse.Listener(
            on_click=self._handleClick,
            on_move=self._handleMove,
            on_scroll=self._handleScroll,
        )
        self._kl.start()
        self._ml.start()

        def unsubscribe():
            self._listeners.remove(handler)
            self._kl.stop()
            self._ml.stop()

        return unsubscribe
