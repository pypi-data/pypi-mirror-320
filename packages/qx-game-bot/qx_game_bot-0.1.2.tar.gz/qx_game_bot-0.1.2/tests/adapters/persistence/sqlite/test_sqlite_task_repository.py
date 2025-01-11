from qx_game_bot.adapters.persistence.sqlite.db import database
from qx_game_bot.adapters.persistence.sqlite.models.task_model import TaskModel
from qx_game_bot.adapters.persistence.sqlite.sqlite_task_repository import (
    SqliteTaskRepository,
)
from qx_game_bot.core.domain.task import Task
from qx_game_bot.core.domain.value_objects.delay_action import DelayAction
from pytest import fixture


@fixture
def task():
    return Task(actions=[DelayAction(timeoutMS=1000)])


@fixture
def repository():
    database.init(":memory:")
    return SqliteTaskRepository()


@fixture(autouse=True)
def saveTask(repository, task):
    repository.save(task)


def test_save(task, repository):
    assert repository.getById(task.id) == task


def test_get_all(task, repository):
    assert repository.getAll() == [task]


def test_remove(task, repository):
    repository.removeById(task.id)
    assert repository.getAll() == []
