from datetime import datetime

from tests.common import DbTestCase
from tests.seeders import UserSeeder, faker
from apps.db_model.models import User
from apps.common.utils import hash_password, check_password


class UserTest(DbTestCase):
    seeders = [
        UserSeeder,
    ]

    def setUp(self) -> None:
        super().setUp()

    def test_registration_success(self):
        user = User.create(
            username=faker.first_name(),
            email=faker.email(),
            password=hash_password(faker.password()),
            status=True,
            date_created=datetime.now(),
        )
        self.assertGreater(user.id, 0)

    def test_login_success(self):
        user = User.get(username="bobst")
        self.assertEqual(UserSeeder.USERNAME, user.username)
        self.assertTrue(
            check_password(UserSeeder.PASSWORD, user.password.encode("utf-8"))
        )
