from __future__ import annotations
import os
import csv
from sqlite3 import Error
from typing import Collection, TYPE_CHECKING

if TYPE_CHECKING:
    from app.form_lib.form_controller import DataTableInfo
    from app.form_lib.models import RegistrationModel


def export_to_csv(form_name: str,
                  table_info: DataTableInfo,
                  entries: Collection[RegistrationModel]) -> str:

    def export_routine(form_name: str, table_info: DataTableInfo, entries: Collection[RegistrationModel]):
        file_path = os.path.realpath(os.getcwd() + '/csv/' + form_name + "_data.csv")
        # Export data into CSV file
        print("Exporting data into CSV")

        # TODO: Ensure that generators work as intended
        # TODO: Ensure that header and rows are generated correctly
        header = table_info.make_header_row()
        rows = [table_info.model_to_row(entry) for entry in entries]

        with open(file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow(header)
            csv_writer.writerows(rows)

        print("Data successfully exported into {}".format(file_path))
        return file_path

    try:
        return export_routine(form_name, table_info, entries)
    except Error as e:
        print(e)

    return ""
