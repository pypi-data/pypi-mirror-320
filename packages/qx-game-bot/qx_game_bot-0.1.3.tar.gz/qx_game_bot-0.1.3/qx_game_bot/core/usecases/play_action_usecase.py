from qx_game_bot.core.domain.task import ActionType
from qx_game_bot.core.ports.action_player import ActionPlayer
from pydantic import BaseModel, Field


class PlayActionUsecase(BaseModel):
    actionPlayer: ActionPlayer
    playedActions: list[ActionPlayer] = Field(default=[])

    def execute(self, action: ActionType):
        self.actionPlayer.play(action)
        self.playedActions.append(action)
