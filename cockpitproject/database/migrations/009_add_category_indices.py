table_name = "sub_category"
index_name = "idx_sub_category_id"


def migrate(migrator, database, fake=False, **kwargs):
    database.execute_sql(
        f'ALTER TABLE {table_name} ADD CONSTRAINT {index_name} '
        'FOREIGN KEY (category_id) REFERENCES category (id)'
    )


def rollback(migrator, database, fake=False, **kwargs):
    database.execute_sql(f'ALTER TABLE `{table_name}` DROP FOREIGN KEY `{index_name}`')
