from typing import List, Optional

from apps.db_model.models import SubCategory


def create_sub_category(sub_category_info: List) -> None:
    """_insert a sub category data on the table _

    Args:
        category (_type_): _description_
    """
    sub_category_item = SubCategory(
        category_id=sub_category_info[1],
        variable_name=sub_category_info[2],
        name=sub_category_info[3],
        unit=sub_category_info[4],
        mini_limit=sub_category_info[5],
        maxi_limit=sub_category_info[6],
    )
    sub_category_item.save()


def update_sub_category(
    id: int, subcategory: str, unit: str, mini_limit: int, maxi_limit: int
) -> None:
    """_update the sub category information_

    Args:
        id (_type_): _description_
        category (_type_): _description_
    """
    sub_category_item = SubCategory.get(SubCategory.id == id)
    sub_category_item.name = subcategory
    sub_category_item.unit = unit
    sub_category_item.mini_limit = mini_limit
    sub_category_item.maxi_limit = maxi_limit
    sub_category_item.save()


def view_sub_category(search_query: Optional[str] = None) -> List:
    """_query the sub category list to show the list on front-end_

    Args:
        search_query (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    sub_category_list = SubCategory.select().order_by(SubCategory.created_at.desc())
    if search_query:
        sub_category_list = SubCategory.where(
            SubCategory.content.contains(search_query)
        )

    return sub_category_list


def delete_sub_category(subcategory: str) -> None:
    """_delete a sub category data_

    Args:
        category (_type_): _description_
    """
    sub_category_item = SubCategory.get(SubCategory.variable_name == subcategory)
    sub_category_item.delete_instance()
