import datetime

from peewee import (
    DateTimeField,
    CharField,
    AutoField,
)

from apps.common.db import BaseModel

table_name = "category"


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class InitialCategrory(BaseModel):
        id = AutoField()
        name = CharField(max_length=50, unique=True, null=False)
        created_at = DateTimeField(default=datetime.datetime.now, null=True)

        class Meta:
            table_name = table_name


def rollback(migrator, database, fake=False, **kwargs):
    @migrator.remove_model
    class InitialCategrory(BaseModel):
        class Meta:
            table_name = table_name
