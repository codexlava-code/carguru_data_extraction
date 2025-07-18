import glob
import shutil
import sys
import os
import logging
import re
from typing import Optional

import peewee

from apps.config import CONFIG
from apps.db_model.models import DumpInfo, MachineData
from datasets.access_data import AccessData
from apps.common.db import db

script_dir = os.path.abspath(os.path.dirname(__file__))
project_dir = os.path.abspath(os.path.dirname(script_dir))
LOG_FILE = os.path.join(script_dir, "loadtodb.log")
PID_FILE = os.path.join(script_dir, "loadtodb.pid")
sys.path.append(script_dir)
sys.path.append(project_dir)
handler = logging.FileHandler(LOG_FILE)
formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger = logging.getLogger("LoadKYCDump")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class ProcessData(AccessData):
    def table_column(self):
        machine_data_column = list(MachineData._meta.fields.keys())
        return machine_data_column

    def filter_column(self, df_machine_data):
        """_summary_"""
        machine_data_column = self.table_column()

        column_data = []
        for df_l in df_machine_data.columns:
            if df_l not in machine_data_column:
                df_machine_data.drop(df_l, axis=1, inplace=True)
            column_data = list(df_machine_data.columns.values)

        df_filter_data = df_machine_data.loc[:, column_data]
        return df_filter_data

    def table_data_insert(self, df_machine_data):
        # BATCH_SIZE = 5000
        # df_filter_data = self.filter_column(df_machine_data)
        # data_records = df_filter_data.to_dict(orient="records")
        BATCH_SIZE = 5000
        df_filter = self.filter_column(df_machine_data)

        df_filter.timestamp = df_filter.timestamp.astype("datetime64[s]")
        # fill null data field with ffill()
        df_filter_fill = df_filter.ffill().bfill()

        data_records = df_filter_fill.to_dict(orient="records")
        for i in range(0, len(data_records), BATCH_SIZE):
            batch = data_records[i : i + BATCH_SIZE]
            with db.atomic():
                try:
                    MachineData.insert_many(batch).execute()
                except peewee.PeeweeException as e:
                    logger.error(f"Error inserting batch: {str(e)}")
                    logger.error(f"Problematic rows in the batch: {batch}")

    def get_path(self, path: str) -> str:
        return AccessData.get_user_path(path)

    def get_date_from_file(self, filename: str) -> str:
        return re.search(r"\d{4}-\d{2}-\d{2}", filename).group()

    def process(self, machine_name: str, machine_id: int) -> Optional[str]:
        """_process the parquet file_
        Args:
            machine_name (str): _description_
            machine_id (str): _description_
        Returns:
            _str_: _description_
        """
        list_to_process = glob.glob(
            self.get_path(CONFIG.get("dump_files")) + f"/{machine_name}*.parquet"
        )
        logger.info("Length of files to be processed %s" % len(list_to_process))
        if len(list_to_process) == 0:
            return "no file to process"
        for filepath in list_to_process:
            try:
                filename = os.path.basename(filepath)
                success_path = "%s/%s" % (CONFIG.get("success_location"), filename)
                unknown_location = self.get_path(CONFIG.get("unknown_location"))
                processed = self.get_path(CONFIG.get("processed_location"))
                failed = self.get_path(CONFIG.get("failed_location"))
                if os.stat(filepath).st_size <= 0:
                    logger.error("%s is empty" % filename)
                    shutil.move(filepath, unknown_location)
                    continue
                if os.path.exists(success_path):
                    logger.error("%s already processed" % filename)
                    shutil.move(filepath, unknown_location)
                    continue
                self.table_data_insert(self.read_local_parquet(machine_id, filepath))
                DumpInfo.create(
                    filename=filename,
                    load_date=self.get_date_from_file(filename),
                    machine_id=machine_id,
                )
                shutil.move(filepath, processed)
            except Exception as exc:
                logger.error(
                    "something went  wrong with file %s  with this error  Desc: %s"
                    % (filename, str(exc))
                )
                shutil.move(filepath, failed)
                continue

    def load_data(self) -> Optional[str]:
        for machine in self.get_machines():
            return self.process(machine.equipment_id, machine.id)
