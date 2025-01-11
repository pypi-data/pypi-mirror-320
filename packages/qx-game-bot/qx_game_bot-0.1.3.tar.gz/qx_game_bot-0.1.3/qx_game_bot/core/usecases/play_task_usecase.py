from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.ports.action_player import ActionPlayer
from pydantic import BaseModel


class PlayTaskUsecase(BaseModel):
    actionPlayer: ActionPlayer

    def execute(self, task: Task):
        for action in task.actions:
            self.actionPlayer.play(action)
