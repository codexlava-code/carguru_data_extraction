import datetime

from peewee import (
    DateTimeField,
    CharField,
    AutoField,
    BooleanField,
)


from apps.common.db import BaseModel

table_name = "user"


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class InitialUser(BaseModel):
        id = AutoField()
        username = CharField(max_length=50, unique=True, null=False)
        email = CharField(max_length=50, unique=True, null=False)
        password = CharField(max_length=80, null=False)
        status = BooleanField(default=True, null=True)
        created_at = DateTimeField(default=datetime.datetime.now, null=True)

        class Meta:
            table_name = table_name


def rollback(migrator, database, fake=False, **kwargs):
    @migrator.remove_model
    class InitialUser(BaseModel):
        class Meta:
            table_name = table_name
