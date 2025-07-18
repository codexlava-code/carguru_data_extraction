from datetime import datetime

from tests.common import DbTestCase
from tests.seeders import MachineSeeder, faker
from apps.db_model.models import Machine


class MachineTest(DbTestCase):
    seeders = [
        MachineSeeder,
    ]

    def setUp(self) -> None:
        super().setUp()

    def test_machine_submission_success(self):
        machine = Machine.create(
            machine_name=faker.first_name(),
            equipment_id=faker.first_name(),
            company_name=faker.first_name(),
            date_created=datetime.now(),
        )
        self.assertGreater(machine.id, 0)

    def test_machine_name_success(self):
        machine_query = Machine.get(equipment_id="GENV23G23")
        self.assertEquals(MachineSeeder.equipment_id, machine_query.equipment_id)
        self.assertTrue(MachineSeeder.machine_name, machine_query.machine_name)
