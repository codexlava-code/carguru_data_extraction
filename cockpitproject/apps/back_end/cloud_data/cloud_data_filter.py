from typing import List, Optional
from datetime import datetime, timedelta

from peewee import fn
import pandas as pd
from pandas import DataFrame
from memoization import cached, CachingAlgorithmFlag

from datasets.access_data import AccessData
from apps.back_end.utils.notification_callback import notify_message
from apps.db_model.models import Machine, MachineData


class CloudFilter(AccessData):
    """_Cloud all data filter to use on frontend_"""

    def __init__(
        self,
        platform_id: str = "",
        equipment_id: str = "",
        dflt_start_date: Optional[datetime] = None,
        dflt_end_date: Optional[datetime] = None,
    ):
        self.platform_id = platform_id
        self.equipment_id = equipment_id
        self.dflt_start_date = dflt_start_date
        self.dflt_end_date = dflt_end_date
        self.date_range_df = pd.to_datetime(
            [self.dflt_start_date, self.dflt_end_date], format="%Y-%m-%d"
        )

    def get_platform_id(self) -> str:
        return self.platform_id

    def get_equipment_id(self) -> str:
        return self.equipment_id

    def column_data(self) -> List:
        """_removing all unique value, so that will not less than 2 values_
        Returns:
            _list_: _returning a list column data_
        """

        df_list_data = []
        try:
            df_list_data = self.db_machine_data(
                self.equipment_id, self.date_range_df[0].date()
            )
        except Exception as error:
            message = "timestamp isn't exist:" + str(error) + "\n"
            notify_message(message)

        df_list_data.drop(
            columns=[
                "datasource",
                "machineid",
                "currenttime",
                "boatpower",
                "activemonitorreadings",
                "wirefeedrate",
                "mfc_flow2",
                "mfc_flow",
                "totalmachinetime",
                "totalrunningtime",
                "machinespeed",
                "machinestate",
                "totalproductiontime",
                "id",
                "created_at",
            ],
            axis=1,
            inplace=True,
            errors="ignore",
        )

        column_data = []
        for col in df_list_data.columns:
            column_data = list(df_list_data.columns.values)
        return column_data

    def get_categories(self) -> DataFrame:
        """_get categories list data_
        Returns:
            _list_: _categories list data_
        """
        df_list_data = []
        try:
            df_list_data = self.db_machine_data(
                self.equipment_id,
                self.date_range_df[0].date(),
                df_columns=self.column_data(),
            )
        except Exception as error:
            message = "timestamp isn't exist:" + str(error) + "\n"
            notify_message(message)

        # classification file setup categories and subcategories
        df_cat_classify = []
        try:
            # import categories and subcategories list
            df_cat_classify = pd.read_csv("datasets/variable_classification.csv")
        except Exception as error:
            print(f"classification file not exist: {error}")
            message = "classification file not exist :" + str(error) + "\n"
            notify_message(message)

        # making a group categories list
        dict_groups = {}
        df_section = df_cat_classify.loc[:, ["Subcat", "Categories"]]
        df_categories = df_section.groupby("Categories")
        for cat, group in df_categories:
            for col in group.Subcat.values:
                dict_groups[str.lower(col)] = cat
        # making categories from df data columns
        df_category = pd.melt(
            df_list_data.drop_duplicates("timestamp"), id_vars=["timestamp"]
        )
        # drop timestamp and value
        df_category.drop(
            columns=["timestamp", "value"],
            axis=1,
            inplace=True,
            errors="ignore",
        )
        df_category.loc[:, "category"] = df_category.loc[:, "variable"].apply(
            lambda v: dict_groups.get(v, "no category")
        )
        return df_category

    def calendar_date_range(self) -> List[str]:
        """_it's transfer the date-range date to the front-end calendar_

        Returns:
            _class_: _pandas datetime data_
        """
        machine_id = (
            Machine.select().where(Machine.equipment_id == self.equipment_id).first()
        )
        machine_data_query = (
            (
                MachineData.select(
                    fn.MIN(MachineData.timestamp.cast("date")).alias("min_date"),
                    fn.MAX(MachineData.timestamp.cast("date")).alias("max_date"),
                )
            )
            .where(MachineData.machine_id == machine_id.id)
            .first()
        )
        return machine_data_query.min_date, machine_data_query.max_date

    @cached(ttl=86400, algorithm=CachingAlgorithmFlag.LFU)
    def get_date_range(self) -> DataFrame:
        """_get datetime bring data from cloud_
        Args:
            start_date_g (_datetime_): _start date from selector_
            end_date_g (_type_): _end date from selector_

        Returns:
            _list_: _all selected days data return_
        """
        # make dataframe for days data bring from blob storage
        first_date = self.date_range_df[0].date()
        last_date = self.date_range_df[1].date()

        df_days = []
        for day in range((last_date - first_date).days + 1):
            day = first_date + timedelta(day)
            data = self.db_machine_data(
                self.equipment_id, day, df_columns=self.column_data()
            )
            if data is None:
                continue
            df_days.append(data)
        try:
            df_days = pd.concat(df_days)
            # removed unwanted data from df columns
            df_days.timestamp = df_days.timestamp.astype("datetime64[s]")
            df_days.set_index("timestamp", inplace=True, drop=False)
        except Exception as error:
            print(f"there is no parquet file date data: {error}")
            message = "there is no parquet file date data:" + str(error) + "\n"
            notify_message(message)
        return df_days

    # @cached(ttl=86400,algorithm=CachingAlgorithmFlag.LFU)
    def get_filter_data(
        self, start_date_g: datetime, end_date_g: datetime, resampling: str
    ) -> List[DataFrame]:
        """_ filter the cloud data based on date range_

        Args:
            start_date_g (_datetime_): _get start date _
            end_date_g (_datetime_): _get end date_

        Returns:
            _list_: _returning data frame days data_
            _list_: _returning data frame filtered data_
        """
        # getting assigned on default instance variable data range
        self.dflt_start_date = start_date_g[0:4] + start_date_g[5:7] + start_date_g[8:]
        self.dflt_end_date = end_date_g[0:4] + end_date_g[5:7] + end_date_g[8:]

        # called the get_date_range() to get date range data
        df_days = self.get_date_range()

        # check for non-numeric data and fill null data field with ffill()
        for column in df_days.columns:
            df_days.loc[:, column] = (
                pd.to_numeric(
                    df_days.loc[:, column], downcast="integer", errors="coerce"
                )
                # .ffill()
                # .bfill()
            )
        # resample data based on time
        df_resample = df_days.resample(resampling).mean()
        # get the decimal point value
        df_resample_dcml = df_resample.round(decimals=4)
        try:
            # read machine section categories and subcategories data
            df_section = pd.read_csv("datasets/variable_classification.csv")
        except Exception as error:
            print(f"classification file isn't exist: {error}")
            message = "classification file isn't exist:" + str(error) + "\n"
            notify_message(message)

        # make a dictionary to get the sub category list
        # use locator to get the specific two column from the excell sheet
        # make all categories list of group to use the groupby()
        # use a for loop to get the group categories name
        cat_groups = {}
        df_section = df_section.loc[:, ["Subcat", "Categories", "Units", "Min", "Max"]]
        df_categories = df_section.groupby("Categories")
        for cat, group in df_categories:
            for col in group.Subcat.values:
                cat_groups[str.lower(col)] = cat

        # use a for loop to get the unit name
        unit_groups = {}
        df_units = df_section.groupby("Units")
        for unit, group in df_units:
            for col in group.Subcat.values:
                unit_groups[str.lower(col)] = unit

        # use a for loop to get the minimum limitation
        min_groups = {}
        df_min = df_section.groupby("Min")
        for min_limit, group in df_min:
            for col in group.Subcat.values:
                min_groups[str.lower(col)] = min_limit

        # use a for loop to get the maximum limitation
        max_groups = {}
        df_max = df_section.groupby("Max")
        for max_limit, group in df_max:
            for col in group.Subcat.values:
                max_groups[str.lower(col)] = max_limit

        # use melt() function to get all columns in variable column and values in value column.
        # In addition, drop all duplicated timestamp
        # change the datetime format of the timestamp
        df_filtered = pd.melt(
            df_resample_dcml.drop_duplicates("timestamp"), id_vars=["timestamp"]
        )
        df_filtered.loc[:, "category"] = df_filtered.loc[:, "variable"].apply(
            lambda v: cat_groups.get(v, "no category")
        )
        df_filtered.loc[:, "unit"] = df_filtered.loc[:, "variable"].apply(
            lambda v: unit_groups.get(v, "")
        )
        df_filtered.loc[:, "min"] = df_filtered.loc[:, "variable"].apply(
            lambda v: min_groups.get(v, "")
        )
        df_filtered.loc[:, "max"] = df_filtered.loc[:, "variable"].apply(
            lambda v: max_groups.get(v, "")
        )
        df_filtered["timestamp"] = pd.to_datetime(
            df_filtered["timestamp"], format="%Y-%m-%d"
        )

        # print(f"cloud filter: {self.platform_id}")
        return df_resample_dcml, df_filtered
