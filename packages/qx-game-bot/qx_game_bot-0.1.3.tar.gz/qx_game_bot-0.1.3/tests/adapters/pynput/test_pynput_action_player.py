from time import sleep
from unittest.mock import NonCallableMock
from qx_game_bot.adapters.pynput.pynput_action_player import PynputActionPlayer
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.domain.value_objects.mouse_move_action import MouseMoveAction
import pynput
from pytest_mock import MockerFixture


class MockMouseController(pynput.mouse.Controller):
    def press(self, button):
        assert isinstance(button, pynput.mouse.Button)

    @property
    def position(self):
        return self._position or (0, 0)

    @position.setter
    def position(self, val):
        assert isinstance(val, tuple)
        assert val == (100, 100)
        self._position = val


def testPynputActionPlayer(mocker: MockerFixture):
    mockSleep = mocker.patch("time.sleep")
    mocker.patch("pynput.mouse.Controller", new=MockMouseController)

    player = PynputActionPlayer()
    player.play(DelayAction(timeoutMS=500))
    player.play(MouseMoveAction(x=100, y=100))

    mockSleep.assert_called_once_with(500 / 1000)
