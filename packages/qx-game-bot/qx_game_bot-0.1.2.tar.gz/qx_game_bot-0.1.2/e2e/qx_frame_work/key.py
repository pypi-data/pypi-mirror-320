from qx_game_bot.adapters.framework.qx_game_bot_framework import (
    QxGameBotFramework,
)

bot = QxGameBotFramework()


def helloAndCopyPaste():
    bot.delay(100).keyTap("enter").keyType("# Hello World")
    bot.keyPress("cmd").keyPress("shift").keyPress("left")
    bot.keyRelease("cmd").keyRelease("shift").keyRelease("left")
    bot.keyTapAll("cmd", "c")
    bot.keyTapAll("cmd", "enter")
    bot.keyTapAll("cmd", "v")
    bot.delay(1500)


def releaseAll():
    bot.keyPress("enter").keyPress("backspace").keyReleaseAll()
    bot.keyType("write some thing wrong").delay(500)
    bot.keyPress("alt").keyPress("backspace").keyReleaseAll().keyTap("backspace")


def clickOnMatchedImg():
    result = bot.matchImgOnScreen("example.png", 0.75, retryDuration=1000)
    if not result:
        print("No match")
    bot.click(result, position="center")


helloAndCopyPaste()
releaseAll()
