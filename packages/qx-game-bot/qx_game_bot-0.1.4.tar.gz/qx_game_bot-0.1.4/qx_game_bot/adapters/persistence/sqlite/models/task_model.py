from datetime import datetime
from uuid import uuid4
from qx_game_bot.adapters.persistence.sqlite.db import database
from peewee import *


class TaskModel(Model):
    id = UUIDField(default=uuid4, primary_key=True)
    createdAt = DateTimeField(default=datetime.now)
    taskName = TextField()
    actions = TextField(default="[]")

    class Meta:
        database = database
