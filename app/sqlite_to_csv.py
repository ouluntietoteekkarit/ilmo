import sqlite3 as sql
import os
import csv
from sqlite3 import Error, Connection


def export_to_csv(table_name: str):
    def export_routine(table: str, connection: Connection):
        file_path = os.path.realpath(os.getcwd() + '/csv/' + table + "_data.csv")
        # Export data into CSV file
        print("Exporting data into CSV")

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM " + table)
        with open(file_path, "w", newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",", )
            csv_writer.writerow([i[0] for i in cursor.description])
            csv_writer.writerows(cursor)

        print("Data successfully exported into {}".format(file_path))
        return file_path

    try:
        conn = sql.connect('app.db')
    except Error as e:
        print(e)
        return

    path = ""
    try:
        path = export_routine(table_name, conn)
    except Error as e:
        print(e)

    conn.close()
    return path
