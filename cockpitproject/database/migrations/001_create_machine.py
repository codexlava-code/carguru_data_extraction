from peewee import (
    DateTimeField,
    CharField,
    AutoField,
)

from apps.common.db import BaseModel

import datetime

table_name = "machine"


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class InitialMachine(BaseModel):
        id = AutoField()
        machine_name = CharField(max_length=50, unique=True, null=False)
        equipment_id = CharField(max_length=50, unique=True, null=False)
        company_name = CharField(max_length=50, null=False)
        created_at = DateTimeField(default=datetime.datetime.now, null=True)

        class Meta:
            table_name = table_name


def rollback(migrator, database, fake=False, **kwargs):
    @migrator.remove_model
    class InitialMachine(BaseModel):
        class Meta:
            table_name = table_name
