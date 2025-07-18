import datetime

from peewee import (
    DateTimeField,
    CharField,
    ForeignKeyField,
    AutoField,
    IntegerField, FloatField,
)

from apps.common.db import BaseModel

from apps.db_model.models import Category

table_name = "sub_category"


def migrate(migrator, database, fake=False, **kwargs):
    @migrator.create_model
    class InitialSubCategory(BaseModel):
        id = AutoField()
        category_id = ForeignKeyField(Category, backref="subcategories", null=False)
        name = CharField(unique=True, max_length=100, null=False)
        variable_name = CharField(unique=True, max_length=100, null=False)
        unit = CharField(max_length=50, null=True)
        mini_limit = FloatField(null=True)
        maxi_limit = FloatField(null=True)
        created_at = DateTimeField(default=datetime.datetime.now, null=True)

        class Meta:
            table_name = table_name


def rollback(migrator, database, fake=False, **kwargs):
    @migrator.remove_model
    class InitialSubCategory(BaseModel):
        class Meta:
            table_name = table_name
