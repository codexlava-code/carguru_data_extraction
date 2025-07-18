from typing import List
from datetime import datetime

from faker import Faker

from apps.db_model.models import User, Machine
from apps.common.utils import hash_password

faker = Faker()


def seed(model, seed_list: List[dict], truncate: bool = True):
    if truncate:
        model.truncate_table()
    model.bulk_create([model(**item) for item in seed_list])


class BaseSeeder:
    _model_class = None
    _seeds = []
    _dt_now = datetime.now()

    @property
    def model_class(self):
        if not self._model_class:
            raise SystemError("No model provided for base seeder")
        return self._model_class

    def run(self):
        seed(self.model_class, self._seeds)

    def truncate(self):
        self.model_class.truncate_table()


class UserSeeder(BaseSeeder):
    _model_class = User
    USERNAME = "bobst"
    PASSWORD = "bobst123"

    @property
    def _seeds(self) -> list[dict]:
        return [
            {
                "username": self.USERNAME,
                "email": "bobst@bobst.com",
                "password": hash_password(self.PASSWORD),
                "status": True,
                "created_at": datetime.now(),
            }
        ]


class MachineSeeder(BaseSeeder):
    _model_class = Machine
    machine_name = "rambert"
    equipment_id = "GENV23G23"
    company_name = "Manchester R&D"

    @property
    def _seeds(self) -> list[dict]:
        return [
            {
                "machine_name": self.machine_name,
                "equipment_id": self.equipment_id,
                "company_name": self.company_name,
                "created_at": datetime.now(),
            }
        ]
