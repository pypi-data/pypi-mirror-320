from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()

res = bot.imgOcr("e2e/ocr/image.png")
print(res)
