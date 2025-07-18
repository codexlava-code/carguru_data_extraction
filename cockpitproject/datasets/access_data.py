import io
import os
from typing import Union, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps

import pandas as pd
from azure.core.exceptions import ResourceNotFoundError, ResourceExistsError
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient, ContainerClient
from pandas import DataFrame

from apps.config import CONFIG
from apps.db_model.models import Machine, MachineData
from datasets.base_class import BaseData


def exception_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ResourceNotFoundError as e:
            # Handle the ResourceNotFoundError exception here, e.g., log the error message
            print(f"ResourceNotFoundError: {str(e)}")
        except Exception:
            # Allow other exceptions to propagate
            raise

    return wrapper


class AccessData(BaseData):
    """_access the azure storage data_

    Args:
        BaseData (_type_): _description_
    """

    def get_machines(self) -> Optional[Machine]:
        return Machine.select()

    @staticmethod
    def client() -> ContainerClient:
        """
        Instantiate the blob service client using different credentials based on the environment.

        Uses DefaultAzureCredential for local development (Managed Identity) and
        ClientSecretCredential with Service Principal for production.

        Returns:
            BlobServiceClient: An instance of BlobServiceClient for interacting with Azure Blob Storage.
        """
        if CONFIG.get("ENVIRONMENT") == "DEVELOPMENT":
            client_credential = DefaultAzureCredential()
        else:
            tenant_id = CONFIG.get("AZURE_TENANT_ID")
            client_id = CONFIG.get("AZURE_CLIENT_ID")
            client_secret = CONFIG.get("AZURE_CLIENT_SECRET")
            client_credential = ClientSecretCredential(
                tenant_id, client_id, client_secret
            )
        # pass the blob sevice client access
        account_url = CONFIG.get("AZURE_STORAGE_ACCOUNT_URL")
        blob_service_client = BlobServiceClient(
            account_url, credential=client_credential
        )
        # print(blob_service_client)
        return blob_service_client.get_container_client(
            CONFIG.get("AZURE_CONTAINER_NAME")
        )

    def process(self, machine: str, machine_id: str) -> Optional[str]:
        pass

    #  @cached(ttl=86400,algorithm=CachingAlgorithmFlag.LFU)
    def read_data(
        self,
        platform_id: str,
        machine_id: str,
        date_range: datetime,
        columns=None,
        **kwargs,
    ) -> Union[None, List]:
        """_Read parquet data_

        Args:
            platform_id (str): _get platform id number_
            machine_id (str): _get machine id number_
            date_range (_timestamp_): _get the one
             day date_range for get the columns list_
            columns (_str_, optional): _get the column
            list without default column_. Defaults to None.

        Returns:
            _str_: _if file not exist return the information_
        """
        path_location = AccessData._get_path(
            platform_id, machine_id, date_range, **kwargs
        )

        blob_data_list = self.client().get_blob_client(path_location)
        exists = blob_data_list.exists()

        if exists:
            try:
                blob_data = blob_data_list.download_blob()
                if columns is None:
                    data_list = pd.read_parquet(
                        io.BytesIO(blob_data.readall()), engine="fastparquet"
                    )
                else:
                    data_list = pd.read_parquet(
                        io.BytesIO(blob_data.readall()),
                        columns=columns,
                        engine="fastparquet",
                    )
                return data_list

            except Exception:
                # TODO: log exception
                pass
        else:
            # TODO: Update this when the UI has been pointed to DB
            pass
        return None

    @staticmethod
    def _get_path(
        platform_id: str, machine_id: str, date_range: datetime, **kwargs
    ) -> str:
        """_get the machine data path link_

        Args:
            platform_id (_str_): _get platform id number_
            machine_id (_str_): _get machine id number_
            date_range (_timestamp_): _get timestamp range_

        Returns:
            _str_: _return the path link_
        """
        file_name = "variables-" + str(date_range)[:19] + ".parquet"
        path = (
            platform_id
            + "/variables/"
            + machine_id
            + "/"
            + str(date_range.year)
            + "/"
            + file_name
        )
        return path

    @staticmethod
    def get_previous_day_blob_names(machine_id: str, off_set: str = None):
        """
        Generates blob names based on the previous day's date.

        Assumes a specific naming convention and directory structure for the blobs.

        Returns:
            Tuple[str, str]: A tuple containing the base path and the blob name.
        """
        # Calculate yesterday's date
        if off_set is None:
            off_set = (datetime.now() - timedelta(days=1)).date().isoformat()

        # Construct the blob path and name based on the ISO date
        base_path = f"K5METALLIZER/variables/{machine_id}/{off_set[:4]}"
        blob_name = f"variables-{off_set}.parquet"
        return base_path, blob_name

    def download_previous_day(self) -> None:
        """Download data for the previous day."""

        for machine in self.get_machines():
            base_path, blob_name = AccessData.get_previous_day_blob_names(
                machine.equipment_id
            )
            self.download_blob_file(base_path, blob_name, machine.equipment_id)

    def download_previous_months(self, month_count: int) -> None:
        """Download data for the previous months."""

        for machine in self.get_machines():
            for date in self.iterate_dates_last_six_months(month_count):
                try:
                    print(date)
                    base_path, blob_name = AccessData.get_previous_day_blob_names(
                        machine.equipment_id, date
                    )
                    self.download_blob_file(base_path, blob_name, machine.equipment_id)
                except Exception as e:
                    print(f"An error occurred: {str(e)}")

    def iterate_dates_last_six_months(self, number_of_months: int):
        today = datetime.now().date()
        date_list = []

        for _ in range(number_of_months):
            # Calculate the first day of the current month
            first_day_current_month = today.replace(day=1)

            # Calculate the last day of the current month
            if first_day_current_month.month == 12:
                last_day_current_month = first_day_current_month.replace(day=31)
            else:
                last_day_current_month = first_day_current_month.replace(
                    day=1, month=first_day_current_month.month + 1
                ) - timedelta(days=1)

            # Add dates within the current month to the list
            while first_day_current_month <= last_day_current_month:
                date_list.append(first_day_current_month.isoformat())
                first_day_current_month += timedelta(days=1)

            # Move back one month
            today = today.replace(day=1) - timedelta(days=1)

        return date_list

    def download_blob_file(self, base_path: str, blob_name: str, machine_name: str):
        """
        Downloads a specified blob from Azure Blob Storage.

        Args:
            blob_service_client (BlobServiceClient): The client to interact with the Blob Storage.
            container_name (str): Name of the blob container.
            blob_name (str): Name of the blob to be downloaded.
            local_file_name (str): Local path to save the downloaded file.
        """
        full_blob_name = f"{base_path}/{blob_name}"
        dump_location = "%s/%s" % (
            CONFIG.get("dump_files"),
            machine_name + "-" + blob_name,
        )

        try:
            # Retrieve the blob client for the specific blob
            blob_client = self.client().get_blob_client(full_blob_name)
            download_stream = blob_client.download_blob()

            # Write the blob content to a local file
            with open(AccessData.get_user_path(dump_location), "wb") as file:
                file.write(download_stream.readall())
        except ResourceExistsError as e:
            print(f"Error occurred while downloading {blob_name}: {e}")
            # We throw the exception again so that the script fails
            raise e

    @staticmethod
    def read_local_parquet(machine_id: int, file_path: str) -> List:
        try:
            data_list = pd.read_parquet(file_path, engine="fastparquet")
            data_list["machine_id"] = machine_id

        except Exception as e:
            print(f"parquet file can't read {e}")
            raise e
        return data_list

    @staticmethod
    def get_user_path(path: str) -> str:
        return os.path.join(os.path.expanduser("~"), path)

    def db_machine_data(
        self,
        equipmnt_id: str,
        date_range: datetime,
        df_columns: Optional[List[Any]] = None,
    ) -> DataFrame:
        """_get database machine data_"""
        obj_machine = (
            Machine.select().where(Machine.equipment_id == equipmnt_id).first()
        )
        machine_data_query = MachineData.select().where(
            MachineData.machine_id == obj_machine.id,
            MachineData.timestamp.cast("date") == date_range,
        )
        # check column exist or not exist
        db_dataframe = []
        if df_columns:
            machine_data_query = MachineData.select(
                *[getattr(MachineData, column) for column in df_columns]
            ).where(
                MachineData.machine_id == obj_machine.id,
                MachineData.timestamp.cast("date") == date_range,
            )
            db_dataframe = pd.DataFrame(list(machine_data_query.dicts()))
        else:
            machine_data_query = (
                MachineData.select()
                .where(
                    MachineData.machine_id == obj_machine.id,
                    MachineData.timestamp.cast("date") == date_range,
                )
                .limit(1)
            )
            db_dataframe = pd.DataFrame(list(machine_data_query.dicts()))
        return db_dataframe
