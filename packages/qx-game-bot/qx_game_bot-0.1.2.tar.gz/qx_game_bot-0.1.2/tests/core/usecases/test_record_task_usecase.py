from pydantic import InstanceOf
from pytest import fixture
from pytest_mock import MockFixture, MockerFixture

from qx_game_bot.adapters.persistence.sqlite.db import database
from qx_game_bot.adapters.persistence.sqlite.sqlite_task_repository import (
    SqliteTaskRepository,
)
from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from qx_game_bot.core.ports.keyboard_mouse_listener import KeyboardMouseListener
from qx_game_bot.core.usecases.record_task_usecase import RecordTaskUsecase


@fixture
def taskRepository():
    database.init(":memory:")
    return SqliteTaskRepository()


@fixture
def keyboardMouseActionListener():
    class Listener(KeyboardMouseListener):
        def onAction(self, handleAction):
            handleAction(DelayAction(timeoutMS=500))

            def unsubscribe():
                pass

            return unsubscribe

    return Listener()


@fixture
def recordTaskUsecase(taskRepository, keyboardMouseActionListener):
    return RecordTaskUsecase(
        taskRepository=taskRepository,
        keyboardMouseActionListener=keyboardMouseActionListener,
    )


def testRecordTaskUsecase(recordTaskUsecase, taskRepository, mocker: MockerFixture):
    stop = recordTaskUsecase.execute()
    stop()
    tasks = taskRepository.getAll()
    assert isinstance(tasks[0], Task)
    assert tasks[0].actions[0] == DelayAction(timeoutMS=500)
