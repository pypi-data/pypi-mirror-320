from time import sleep
from qx_game_bot.adapters.pynput.pynput_keyboard_mouse_listener import (
    PynputKeyboardMouseListener,
)
from qx_game_bot.core.domain.value_objects.key_press_action import KeyPressAction
from pytest import fixture
from pytest_mock import MockerFixture
from pynput.keyboard import Key, KeyCode
from pynput.mouse import Button


@fixture
def mockKeyboardListener(mocker: MockerFixture):
    mockListener = mocker.patch("pynput.keyboard.Listener")
    return mockListener


@fixture
def mockMouseListener(mocker: MockerFixture):
    mockListener = mocker.patch("pynput.mouse.Listener")
    return mockListener


def test_on_action(mocker: MockerFixture, mockKeyboardListener, mockMouseListener):
    listener = PynputKeyboardMouseListener()
    stub = mocker.stub()
    listener.onAction(stub)
    mockKeyboardListener.call_args.kwargs["on_press"](key=KeyCode.from_char("a"))
    stub.assert_called()
