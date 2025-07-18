from peewee import (
    MySQLDatabase,
    Model,
)

from apps.common.db_config import DBConfig

db_config = DBConfig()


db = MySQLDatabase(
    db_config.db_name,
    user=db_config.db_username,
    password=db_config.db_password,
    host=db_config.db_endpoint,
    port=int(db_config.port),
)


class BaseModel(Model):
    class Meta:
        database = db
