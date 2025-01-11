import pynput
from qx_game_bot.core.ports.global_hot_keys import GlobalHotKeys


class PynputGlobalHotKeys(GlobalHotKeys):
    def bind(self, config):
        subscription = pynput.keyboard.GlobalHotKeys(config)
        subscription.start()

        return subscription
