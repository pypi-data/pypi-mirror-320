import cv2
from mss import mss
import numpy as np
from qx_game_bot.core.domain.value_objects.img import Img
from qx_game_bot.core.ports.screenshot import Screenshot


class MssScreenshot(Screenshot):
    def model_post_init(self, __context):
        super().model_post_init(__context)
        self._sct = mss()

    def grab(self, monitor):
        if not monitor:
            monitor = self._sct.monitors[1]
        elif isinstance(monitor, int):
            monitor = self._sct.monitors[monitor]
        grabbedImg = self._sct.grab(monitor)
        width = grabbedImg.width
        height = grabbedImg.height
        imgArr = np.array(grabbedImg)
        imgArr = cv2.cvtColor(imgArr, cv2.COLOR_BGRA2BGR)
        img = Img(img=imgArr, width=width, height=height)
        return img
