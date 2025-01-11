from qx_game_bot.adapters.framework.qx_game_bot_framework import QxGameBotFramework


bot = QxGameBotFramework()

# 双击左键 (100, 100)
bot.mouseClick("left", x=100, y=100, count=2)
# 移动到
bot.mouseMoveTo(500, 500)
# 滚动 y：500
bot.mouseScrollBy(0, dy=500)
