import sys


sys.path.append(".")
from qx_game_bot.adapters.pynput.pynput_global_hot_keys import PynputGlobalHotKeys


globalHostKeys = PynputGlobalHotKeys()
binding = globalHostKeys.bind(
    {"<ctrl>+a": lambda: print("hello"), "<esc>": lambda: binding.stop()}
)
binding.join()
