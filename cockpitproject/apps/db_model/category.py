from typing import List, Optional

from apps.db_model.models import Category


def create_category(category: str) -> None:
    """_insert a category data on the table _

    Args:
        category (_type_): _description_
    """
    category_item = Category(name=category)
    category_item.save()


def update_category(id: str, category: str) -> None:
    """_update the category information_

    Args:
        id (_type_): _description_
        category (_type_): _description_
    """
    category_item = Category.get(Category.id == id)
    category_item.name = category
    category_item.save()


def view_category(search_query: Optional[str] = None) -> List:
    """_query the category list to show the list on front-end_

    Args:
        search_query (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    category_list = Category.select().order_by(Category.created_at.desc())
    if search_query:
        category_list = Category.where(Category.content.contains(search_query))

    return category_list


def delete_category(category: str) -> None:
    """_delete a category data_

    Args:
        category (_type_): _description_
    """
    category_item = Category.get(Category.name == category)
    category_item.delete_instance()
