import sys
from pathlib import Path

sys.path.append(".")

from qx_game_bot.adapters.persistence.sqlite.db import initSqliteFileDatabase
from qx_game_bot.adapters.persistence.sqlite.sqlite_task_repository import (
    SqliteTaskRepository,
)
from qx_game_bot.adapters.pynput.pynput_action_player import PynputActionPlayer
from qx_game_bot.core.usecases.get_task_usecase import GetTaskUsecase
from qx_game_bot.core.usecases.play_task_usecase import PlayTaskUsecase

if __name__ == "__main__":
    filepath = (Path(__file__).parent / "./e2e.db").absolute()
    initSqliteFileDatabase(filepath)
    taskRepository = SqliteTaskRepository()
    actionPlayer = PynputActionPlayer()

    playUsecase = PlayTaskUsecase(
        actionPlayer=actionPlayer, taskRepository=taskRepository
    )

    playUsecase.execute()
