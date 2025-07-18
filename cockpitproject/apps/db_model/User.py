from typing import List, Optional

from apps.common.utils import hash_password
from apps.db_model.models import User


def create_user(user_info: List) -> None:
    """_register new user_

    Args:
        user_info (_list_): _get user information_
    """
    User(
        username=user_info[1], password=hash_password(user_info[2]), email=user_info[3]
    ).save()


def view_user(search_query: Optional[str] = None) -> List[None | List]:
    """_show user information_"""
    user_list = User.select().order_by(User.created_at.desc())
    if search_query:
        user_list = User.where(User.content.contains(search_query))
    return user_list


def update_user(id: str, machine: str) -> None:
    """_update the user information_

    Args:
        id (_type_): _description_
        machine (_type_): _description_
    """
    machine_item = User.get(User.id == id)
    machine_item.name = machine
    machine_item.save()


def delete_user(username: str) -> None:
    """_delete the user_

    Args:
        username (_string_): _get username delete user_
    """
    User.get(User.username == username).delete_instance()
