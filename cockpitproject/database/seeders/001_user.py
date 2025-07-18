from datetime import datetime

from apps.db_model.models import User, seed
from apps.common.utils import hash_password


def seed_items():
    seed(
        User,
        [
            {
                "username": "bobstd",
                "email": "bobstd@bobst.com",
                "password": hash_password("bobst123"),
                "status": True,
                "created_at": datetime.now(),
            }
        ],
    )
