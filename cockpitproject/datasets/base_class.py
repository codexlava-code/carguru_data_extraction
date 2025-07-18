from abc import ABC, abstractmethod
from functools import wraps
from typing import Optional, List


def handle_exception_and_continue(exception_type):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except exception_type:
                pass

        return wrapper

    return decorator


class BaseData(ABC):
    @abstractmethod
    def download_previous_day(self) -> None:
        pass

    @abstractmethod
    def download_previous_months(self, month_count: int) -> None:
        pass

    @abstractmethod
    def process(self, machine: str, machine_id: str) -> Optional[str]:
        pass

    @abstractmethod
    def db_machine_data(
        self, equipment_id: str, date_range: str, df_columns: List = []
    ) -> List:
        pass
