from pathlib import Path
from pprint import pprint
import sys
from time import sleep

sys.path.append(".")
""""""

from qx_game_bot.adapters.pynput.pynput_action_player import PynputActionPlayer
from qx_game_bot.core.usecases.play_task_usecase import PlayTaskUsecase


from qx_game_bot.adapters.persistence.sqlite.sqlite_task_repository import (
    SqliteTaskRepository,
)

from qx_game_bot.adapters.persistence.sqlite.db import (
    initSqliteFileDatabase,
)
from qx_game_bot.adapters.pynput.pynput_keyboard_mouse_listener import (
    PynputKeyboardMouseListener,
)
from qx_game_bot.core.usecases.record_task_usecase import RecordTaskUsecase


if __name__ == "__main__":
    filepath = (Path(__file__).parent / "./e2e.db").absolute()
    initSqliteFileDatabase(filepath)
    taskRepository = SqliteTaskRepository()
    keyboardMouseListener = PynputKeyboardMouseListener()
    recordUsecase = RecordTaskUsecase(
        taskRepository=taskRepository, keyboardMouseActionListener=keyboardMouseListener
    )
    actionPlayer = PynputActionPlayer()
    playUsecase = PlayTaskUsecase(actionPlayer=actionPlayer)
    print("Start recording...".center(40, "-"))
    stop = recordUsecase.execute()

    sleep(2)
    task = stop()
    pprint(task.actions)
    print("Recording stopped".center(40, "-"))
