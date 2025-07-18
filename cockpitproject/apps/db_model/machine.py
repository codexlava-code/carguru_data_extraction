from typing import List, Optional

from apps.db_model.models import Machine


def create_machine(machine: List) -> None:
    """_insert a machine data on the table _

    Args:
        category (_type_): _description_
    """

    Machine(
        machine_name=machine[1],
        equipment_id=machine[2].upper(),
        company_name=machine[3],
    ).save()


def update_machine(id: str, machine: List) -> None:
    """_update the machine information_

    Args:
        id (_type_): _description_
        machine (_type_): _description_
    """
    machine_item = Machine.get(Machine.id == id)
    machine_item.machine_name = machine[1]
    machine_item.equipment_id = machine[2].upper()
    machine_item.company_name = machine[3]
    machine_item.save()


def view_machine(search_query: Optional[str] = None) -> List:
    """_query the machine list to show the list on front-end_

    Args:
        search_query (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """
    machine_list = Machine.select().order_by(Machine.created_at.desc())
    if search_query:
        machine_list = Machine.where(Machine.content.contains(search_query))

    return machine_list


def delete_machine(machine: str) -> None:
    """_delete a machine data_

    Args:
        machine (_type_): _description_
    """
    machine_item = Machine.get(Machine.equipment_id == machine)
    machine_item.delete_instance()
