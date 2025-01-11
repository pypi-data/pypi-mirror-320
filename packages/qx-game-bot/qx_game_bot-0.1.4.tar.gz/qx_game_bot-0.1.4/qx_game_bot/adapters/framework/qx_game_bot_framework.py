from typing import Literal
import numpy as np

from qx_game_bot.adapters.cv.cv_color_matcher import CvColorMatcher
from qx_game_bot.adapters.cv.cv_template_matcher import CvTemplateMatcher
from qx_game_bot.adapters.mss.mss_screenshot import MssScreenshot
from qx_game_bot.adapters.paddleocr.paddle_ocr import PaddleOcr
from qx_game_bot.adapters.persistence.sqlite import db
from qx_game_bot.adapters.persistence.sqlite.sqlite_task_repository import (
    SqliteTaskRepository,
)
from qx_game_bot.adapters.pynput.pynput_action_player import PynputActionPlayer
from qx_game_bot.adapters.pynput.pynput_keyboard_mouse_listener import (
    PynputKeyboardMouseListener,
)
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.domain.value_objects.key_press_action import KeyPressAction
from qx_game_bot.core.domain.value_objects.key_release_action import KeyReleaseAction
from qx_game_bot.core.domain.value_objects.key_tap_action import KeyTapAction
from qx_game_bot.core.domain.value_objects.key_type_action import KeyTypeAction
from qx_game_bot.core.domain.value_objects.mouse_move_action import MouseMoveAction
from qx_game_bot.core.domain.value_objects.mouse_press_action import MousePressAction
from qx_game_bot.core.domain.value_objects.mouse_release_action import (
    MouseReleaseAction,
)
from qx_game_bot.core.domain.value_objects.mouse_scroll_action import MouseScrollAction
from qx_game_bot.core.domain.value_objects.mouse_tap_action import MouseTapAction
from qx_game_bot.core.ports.screenshot import MonitorRegion
from qx_game_bot.core.usecases.img_ocr_usecase import ImgOcrUsecase
from qx_game_bot.core.usecases.match_all_screen_usecase import MatchAllScreenUsecase
from qx_game_bot.core.usecases.match_all_templates_usecase import (
    MatchAllTemplatesUsecase,
)
from qx_game_bot.core.usecases.match_screen_color_point_usecase import (
    MatchScreenColorPointUsecase,
)
from qx_game_bot.core.usecases.match_screen_usecase import MatchScreenUsecase
from qx_game_bot.core.usecases.match_template_usecase import MatchTemplateUsecase
from qx_game_bot.core.usecases.play_action_usecase import PlayActionUsecase
from qx_game_bot.core.usecases.play_task_usecase import PlayTaskUsecase
from qx_game_bot.core.usecases.record_task_usecase import RecordTaskUsecase
from qx_game_bot.core.usecases.screen_ocr_usecase import ScreenOcrUsecase


class QxGameBotFramework:
    def __init__(
        self,
        dbFilePath: str = ":memory:",
        ocrLang: str | Literal["ch", "en"] = "ch",
    ):
        db.database.init(dbFilePath)
        sqliteTaskRepository = SqliteTaskRepository()
        pynputKeyboardMouseListener = PynputKeyboardMouseListener()
        pynputActionPlayer = PynputActionPlayer()
        cvTemplateMatcher = CvTemplateMatcher()
        mssScreenshot = MssScreenshot()
        cvColorMatcher = CvColorMatcher()
        paddleOcr = PaddleOcr(lang=ocrLang)

        self._recordTaskUsecase = RecordTaskUsecase(
            taskRepository=sqliteTaskRepository,
            keyboardMouseActionListener=pynputKeyboardMouseListener,
        )
        self._playTaskUsecase = PlayTaskUsecase(
            actionPlayer=pynputActionPlayer, taskRepository=sqliteTaskRepository
        )
        self._playActionUsecase = PlayActionUsecase(actionPlayer=pynputActionPlayer)
        self._matchTemplateUsecase = MatchTemplateUsecase(
            templateMatcher=cvTemplateMatcher
        )
        self._matchAllTemplatesUsecase = MatchAllTemplatesUsecase(
            templateMatcher=cvTemplateMatcher
        )
        self._matchScreenUsecase = MatchScreenUsecase(
            templateMatcher=cvTemplateMatcher, screenshot=mssScreenshot
        )
        self._matchAllScreenUsecase = MatchAllScreenUsecase(
            templateMatcher=cvTemplateMatcher, screenshot=mssScreenshot
        )
        self._matchScreenColorPointUsecase = MatchScreenColorPointUsecase(
            colorMatcher=cvColorMatcher, screenshot=mssScreenshot
        )
        self._screenOcrUsecase = ScreenOcrUsecase(
            ocr=paddleOcr, screenshot=mssScreenshot
        )
        self._imgOcrUsecase = ImgOcrUsecase(ocr=paddleOcr)

    def recordTask(self, taskName: str = None):
        stopRecording = self._recordTaskUsecase.execute(taskName)
        return stopRecording

    def playRecordTask(self, taskName: str = None):
        self._playTaskUsecase.execute(taskName=taskName)

    def delay(self, timeoutMS: float):
        self._playActionUsecase.execute(DelayAction(timeoutMS=timeoutMS))
        return self

    def keyPress(self, key: str):
        self._playActionUsecase.execute(KeyPressAction(key=key))
        return self

    def keyRelease(self, key: str):
        self._playActionUsecase.execute(KeyReleaseAction(key=key))
        return self

    def keyReleaseAll(self):
        unReleasedActinons = []
        for action in self._playActionUsecase.playedActions:
            if isinstance(action, KeyPressAction):
                unReleasedActinons.append(action)
            if (
                isinstance(action, KeyReleaseAction)
                and KeyPressAction(**action.model_dump()) in unReleasedActinons
            ):
                unReleasedActinons.remove(KeyPressAction(**action.model_dump()))
        for action in unReleasedActinons:
            self._playActionUsecase.execute(KeyReleaseAction(**action.model_dump()))
        return self

    def keyTap(self, key: str, count: int = 1, intervalMS=None):
        for i in range(count):
            self._playActionUsecase.execute(KeyTapAction(key=key))
            if intervalMS:
                self._playActionUsecase.execute(DelayAction(timeoutMS=intervalMS))
        return self

    def keyTapAll(self, *keys: str, count: int = 1, intervalMS=None):
        for i in range(count):
            for key in keys:
                self._playActionUsecase.execute(KeyPressAction(key=key))
            for key in keys:
                self._playActionUsecase.execute(KeyReleaseAction(key=key))
            if intervalMS:
                self._playActionUsecase.execute(DelayAction(timeoutMS=intervalMS))
        return self

    def keyType(self, string: str, count: int = 1, intervalMS=None):
        for i in range(count):
            self._playActionUsecase.execute(KeyTypeAction(string=string))
            if intervalMS:
                self._playActionUsecase.execute(DelayAction(timeoutMS=intervalMS))
        return self

    def mousePress(
        self,
        button: Literal["left", "right", "middle"],
        x: float = None,
        y: float = None,
    ):
        self._playActionUsecase.execute(MousePressAction(button=button, x=x, y=y))
        return self

    def mouseRelease(
        self,
        button: Literal["left", "right", "middle"],
        x: float = None,
        y: float = None,
    ):
        self._playActionUsecase.execute(MouseReleaseAction(button=button, x=x, y=y))
        return self

    def mouseClick(
        self,
        button: Literal["left", "right", "middle"] = "left",
        x: float = None,
        y: float = None,
        count: int = 1,
        intervalMS=None,
    ):
        for i in range(count):
            self._playActionUsecase.execute(MouseTapAction(button=button, x=x, y=y))
            if intervalMS:
                self._playActionUsecase.execute(DelayAction(timeoutMS=intervalMS))
        return self

    def mouseMoveTo(
        self,
        x: float = None,
        y: float = None,
    ):
        self._playActionUsecase.execute(MouseMoveAction(x=x, y=y))
        return self

    def mouseScrollBy(
        self,
        dx: float = None,
        dy: float = None,
        x: float = None,
        y: float = None,
    ):
        self._playActionUsecase.execute(MouseScrollAction(dx=dx, dy=dy, x=x, y=y))
        return self

    def matchScreen(
        self,
        templateImg: str,
        minConfidence: float | None = 0.9,
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
        monitorRegion: MonitorRegion | None = None,
    ):
        return self._matchScreenUsecase.execute(
            templateImg,
            minConfidence=minConfidence,
            retryCount=retryCount,
            retryIntervalMS=retryIntervalMS,
            monitor=monitorRegion,
        )

    def matchAllScreen(
        self,
        templateImg: str,
        minConfidence: float | None = 0.9,
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
        monitorRegion: MonitorRegion | None = None,
    ):
        return self._matchAllScreenUsecase.execute(
            templateImg,
            minConfidence=minConfidence,
            retryCount=retryCount,
            retryIntervalMS=retryIntervalMS,
            monitor=monitorRegion,
        )

    def matchTemplate(
        self,
        img: str,
        templateImg: str,
        minConfidence: float | None = 0.9,
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
    ):
        return self._matchTemplateUsecase.execute(
            img,
            templateImg,
            minConfidence=minConfidence,
            retryCount=retryCount,
            retryIntervalMS=retryIntervalMS,
        )

    def matchAllTemplates(
        self,
        img: str,
        templateImg: str,
        minConfidence: float | None = 0.9,
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
    ):
        return self._matchAllTemplatesUsecase.execute(
            img,
            templateImg,
            minConfidence=minConfidence,
            retryCount=retryCount,
            retryIntervalMS=retryIntervalMS,
        )

    def matchScreenColorPoint(
        self,
        color: str | tuple[int, int, int],
        x: float,
        y: float,
        minConfidence: float | None = 0.9,
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
    ):
        return self._matchScreenColorPointUsecase.execute(
            x=x,
            y=y,
            color=color,
            minConfidence=minConfidence,
            retryCount=retryCount,
            retryIntervalMS=retryIntervalMS,
        )

    def matchScreenMultiColorPoints(
        self,
        colorPoints: list[str | tuple[int, int, int], int, int],
        minConfidence: float | None = 0.9,
        condition: Literal["allTrue", "oneOfTrue"] = "allTrue",
        retryCount: int | None = None,
        retryIntervalMS: int | None = 200,
    ):
        for color, x, y in colorPoints:
            res = self._matchScreenColorPointUsecase.execute(
                x=x,
                y=y,
                color=color,
                minConfidence=minConfidence,
                retryCount=retryCount,
                retryIntervalMS=retryIntervalMS,
            )
            if condition == "oneOfTrue" and res is True:
                return True
            elif condition == "allTrue" and res is not True:
                return False

        return True

    def screenOcr(
        self,
        returnPosAndScores: bool = False,
        minConfidence=None,
        monitorRegion: MonitorRegion | None = None,
        det_limit_side_len: int = 960,
    ):
        return self._screenOcrUsecase.execute(
            returnPosAndScores=returnPosAndScores,
            minConfidence=minConfidence,
            monitor=monitorRegion,
            det_limit_side_len=det_limit_side_len,
        )

    def imgOcr(
        self,
        img: str,
        returnPosAndScores: bool = False,
        minConfidence=None,
        det_limit_side_len: int = 960,
    ):
        return self._imgOcrUsecase.execute(
            img,
            returnPosAndScores=returnPosAndScores,
            minConfidence=minConfidence,
            det_limit_side_len=det_limit_side_len,
        )
