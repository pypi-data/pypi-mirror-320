# qx-game-bot

Mac, Linux, Windows 跨平台桌面端游戏脚本框架

## 功能

- 键鼠模拟 ✅
- 键鼠录制 ✅
- 屏幕录制 ✅
- 图色匹配 ✅
- 文字OCR识别
- 怪物检测
- 目标跟踪
- 多线程任务
- 基于web的GUI、中控

(先画饼， 慢慢实现...)

## 使用
```py
from qx_game_bot import QxGameBotFramework

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
```
