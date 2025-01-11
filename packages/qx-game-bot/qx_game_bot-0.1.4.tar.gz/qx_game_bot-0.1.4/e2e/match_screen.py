from pathlib import Path
from time import sleep
from timeit import repeat, timeit

import cv2
from numpy import average
from qx_game_bot.adapters.cv.cv_template_matcher import CvTemplateMatcher
from qx_game_bot.adapters.mss.mss_screenshot import MssScreenshot
from qx_game_bot.core.usecases.match_screen_usecase import MatchScreenUsecase

templateMatcher = CvTemplateMatcher(debug=True)
screenshot = MssScreenshot()

matchScreenUsecase = MatchScreenUsecase(
    templateMatcher=templateMatcher, screenshot=screenshot
)

p = Path(__file__).parent / "./apple.png"
filepath = str(p.absolute())


def execution():
    res = matchScreenUsecase.execute(template=filepath)
    print(res)


times = repeat("execution()", "from __main__ import execution", number=1, repeat=20)
print(f"Min: {min(times)}; Max: {max(times)}; Avg: {average(times)}")
