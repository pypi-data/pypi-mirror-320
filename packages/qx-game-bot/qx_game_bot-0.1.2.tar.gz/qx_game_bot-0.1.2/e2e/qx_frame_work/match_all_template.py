from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()

res = bot.matchAllTemplates("e2e/apple.png", "e2e/apple.png")
print(res)
