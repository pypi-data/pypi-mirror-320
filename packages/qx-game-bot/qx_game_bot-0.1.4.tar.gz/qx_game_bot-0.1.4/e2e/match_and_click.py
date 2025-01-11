from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()

res = bot.matchScreen("e2e/apple.png", 0.9, 2)

if res:
    (x, y) = res
    print(x, y)
    bot.mouseClick("left", x=x, y=y)
    bot.mouseMoveTo(100, 500)
    bot.mouseScrollBy(0, -10)
