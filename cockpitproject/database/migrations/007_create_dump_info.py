import datetime

from peewee import DateTimeField, CharField, AutoField, DateField, ForeignKeyField

from apps.common.db import BaseModel
from apps.db_model.models import Machine

table_name = "dump_info"


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class InitialDumpInfo(BaseModel):
        id = AutoField()
        filename = CharField(max_length=50, unique=True)
        load_date = DateField()
        machine_id = ForeignKeyField(Machine, backref="machinedump", null=False)
        created_at = DateTimeField(default=datetime.datetime.now, null=True)

        class Meta:
            table_name = table_name


def rollback(migrator, database, fake=False, **kwargs):
    @migrator.remove_model
    class InitialDumpInfo(BaseModel):
        class Meta:
            table_name = table_name
