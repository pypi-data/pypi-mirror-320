from winreg import HKEY_LOCAL_MACHINE
from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework
from qx_game_bot.adapters.persistence.sqlite import db
from qx_game_bot.adapters.persistence.sqlite.models.task_model import TaskModel


bot = QxGameBotFramework(dbFilePath="e2e/e2e.db")
bot.playRecordTask("task1")
