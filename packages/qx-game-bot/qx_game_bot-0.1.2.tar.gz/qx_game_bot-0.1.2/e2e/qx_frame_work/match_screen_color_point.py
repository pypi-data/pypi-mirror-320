from e2e.utils.measure import measure
from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()


def matchOnePoint():
    res = bot.matchScreenColorPoint("#FFFFFF", 26, 13)
    print(res)


def matchMultiPoints():
    colorPoints = [("CA6179", 1431, 147), ("#FFFFFF", 26, 13)]
    res = bot.matchScreenMultiColorPoints(colorPoints, condition="oneOfTrue")
    print(res)


measure(matchOnePoint)
measure(matchMultiPoints)
