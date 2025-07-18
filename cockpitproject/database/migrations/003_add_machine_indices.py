table_name = "machine_data"
index_name = "idx_machine_data_id"


def migrate(migrator, database, fake=False, **kwargs):
    database.execute_sql(
        f"ALTER TABLE {table_name} ADD CONSTRAINT {index_name}"
        " FOREIGN KEY (machine_id) REFERENCES machine (id)"
    )


def rollback(migrator, database, fake=False, **kwargs):
    database.execute_sql(f'ALTER TABLE {table_name} DROP FOREIGN KEY {index_name}')
