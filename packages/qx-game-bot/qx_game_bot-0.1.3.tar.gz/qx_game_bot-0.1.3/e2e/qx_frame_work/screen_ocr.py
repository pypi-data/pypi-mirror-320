from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()

res = bot.screenOcr(returnPosAndScores=True)

print(res)
