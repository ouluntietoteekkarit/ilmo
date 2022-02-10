import sqlite3 as sql
import os
import csv
from sqlite3 import Error


def exportToCSV(table_name):
    def export_routine(table_name, conn):
        file_path = os.getcwd() + '/csv/' + table_name + "_data.csv"
        # Export data into CSV file
        print("Exporting data into CSV")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM " + table_name)
        with open(file_path, "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow([i[0] for i in cursor.description])
            csv_writer.writerows(cursor)

        print("Data successfully exported into {}".format(file_path))

    try:
        conn = sql.connect('app.db')
    except Error as e:
        print(e)
        return

    try:
        export_routine(table_name, conn)
    except Error as e:
        print(e)

    conn.close()

