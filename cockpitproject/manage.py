import logging
from argparse import ArgumentParser
from os import listdir, path
import importlib

from peewee_migrate import Router

from apps.common.db import db
from bin.load_to_db import ProcessData

BASE_PATH = path.dirname(path.abspath(__file__))

DATABASE_PATH = f"{BASE_PATH}/database"
MIGRATION_DIR = f"{DATABASE_PATH}/migrations"
SEEDER_DIR = f"{DATABASE_PATH}/seeders"


def rollback_all(migration_dir: str, show_print: bool = True) -> None:
    router = Router(db, migration_dir)

    try:
        while not router.rollback():
            pass
    except RuntimeError:
        if show_print:
            print("Rollback finished")


def migrate_all(
    migration_dir: str, show_print: bool = True, show_only_critical_logs: bool = False
) -> None:
    router = Router(db, migration_dir)

    if show_only_critical_logs:
        router.logger.setLevel(logging.CRITICAL)

    for migration in router.run():
        if show_print:
            print(f"Migrations completed: {migration}")


def seed_sample(seeder_dir: str) -> None:
    entries = listdir(seeder_dir)[::-1]

    files = [
        file
        for file in entries
        if path.isfile(path.join(seeder_dir, file))
        and file.endswith(".py")
        and file not in ["__init__.py"]
    ]

    seed_package = seeder_dir.replace(f"{BASE_PATH}/", "").replace("/", ".")

    try:
        # db.execute_sql("SET session_replication_role = 'replica'")

        for file in files:
            seed_module = f'{seed_package}.{file.replace(".py", "")}'
            print(f"Seeding... {file}")
            seeder = importlib.import_module(seed_module)
            seeder.seed_items()
            print(f"Seeded {file}")
    finally:
        # db.execute_sql("SET session_replication_role = 'origin'")
        db.close()


if __name__ == "__main__":
    actions = ["migrate", "rollback", "seed", "download", "process", "download_more"]
    parser = ArgumentParser(description="Run app routines")
    parser.add_argument(
        "--action", type=str, required=True, help="Action to execute", choices=actions
    )
    parser.add_argument(
        "--download-args", nargs="+", help="Additional arguments for the seed action"
    )

    parser_args = parser.parse_args()
    action = parser_args.action

    match action:
        case "migrate":
            migrate_all(MIGRATION_DIR)
        case "rollback":
            rollback_all(MIGRATION_DIR)
        case "seed":
            seed_sample(SEEDER_DIR)
        case "download":
            data = ProcessData()
            data.download_previous_day()
        case "download_more":
            data = ProcessData()
            data.download_previous_months(2)
        case "process":
            data = ProcessData()
            data.load_data()

        case _:
            print("Invalid action specified.")
