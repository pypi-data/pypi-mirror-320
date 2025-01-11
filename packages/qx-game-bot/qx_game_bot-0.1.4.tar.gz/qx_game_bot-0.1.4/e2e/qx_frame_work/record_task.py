from time import sleep
from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework

bot = QxGameBotFramework(dbFilePath="e2e/e2e.db")

stopRecording = bot.recordTask("task1")
sleep(3)
stopRecording()
print("Recording Saved")
