from peewee import chunked

from apps.db_model.models import MachineData
from datasets.access_data import AccessData
from apps.common.db import db


class MachineDataDb:
    def table_column(self):
        # get table column list
        machine_data_column = list(MachineData._meta.fields.keys())
        return machine_data_column

    def machine_column_data(self):
        # call the access data object
        obj_machine_data = AccessData()
        # donload the blob parquet file
        # obj_machine_data.get_machine_and_download()
        # read the downloaded parquet file
        df_machine_data = obj_machine_data.get_machine_and_download(False)
        df_machine_data.timestamp = df_machine_data.timestamp.astype("datetime64")
        # df_machine_data.rename(columns={'machineid': 'machine'}, inplace=True)
        return df_machine_data

    def filter_column(self):
        """_summary_"""
        # Filter the matching column
        df_machine_data = self.machine_column_data()
        machine_data_column = self.table_column()

        column_data = []
        for df_l in df_machine_data.columns:
            if df_l not in machine_data_column:
                df_machine_data.drop(df_l, axis=1, inplace=True)
            column_data = list(df_machine_data.columns.values)

        df_filter_data = df_machine_data.loc[:, column_data]
        return df_filter_data

    def table_data_insert(self):
        df_filter_data = self.filter_column()
        subset_df = df_filter_data.head(100)
        patched_data = subset_df.to_dict(orient="records")
        # print(patched_data)
        ############# normally baching
        # batches = [patched_data[i:i + BATCH_SIZE]
        #         for i in range(0, len(patched_data), BATCH_SIZE)]
        # for batch in batches:
        #     print(batch)
        #     MachineData.insert_many(batch).execute()

        ############## chunked helper function batching
        try:
            with db.atomic():
                for batch in chunked(patched_data, 25):
                    print(batch)
                    MachineData.insert_many(batch).execute()
        except Exception as err:
            print(f"insert error:{err}")


obj_machine_data = MachineDataDb()
filter_data = obj_machine_data.table_data_insert()
