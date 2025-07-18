from unittest import TestCase
from typing import Callable

from manage import BASE_PATH, migrate_all, rollback_all

DATABASE_PATH = f"{BASE_PATH}/database"
MIGRATION_DIR = f"{DATABASE_PATH}/migrations"


class DbTestCase(TestCase):
    seeders = []
    _is_logs_on = False

    @classmethod
    def setUpClass(cls) -> None:
        migrate_all(MIGRATION_DIR, False, True)

    @classmethod
    def tearDownClass(cls) -> None:
        rollback_all(MIGRATION_DIR, False)

    def setUp(self) -> None:
        super().setUp()
        self._run_seeders()
        # self._no_foreign_key_check(self._run_seeders)

    def tearDown(self) -> None:
        super().tearDown()
        self._truncate()

    def _no_foreign_key_check(self, callback: Callable):
        pass
        # try:
        #     db.execute_sql("SET FOREIGN_KEY_CHECKS=0")
        #     callback()
        # finally:
        #     db.execute_sql("SET FOREIGN_KEY_CHECKS=1")

    def _run_seeders(self):
        for seeder in self.seeders:
            seeder().run()

    def _truncate(self):
        for seeder in self.seeders:
            seeder().truncate()
