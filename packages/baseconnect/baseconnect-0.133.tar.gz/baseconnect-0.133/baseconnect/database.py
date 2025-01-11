# my_database_lib/database.py

import pyodbc
import pandas as pd


class Database:
    def __init__(self, server, database, user=None, password=None, driver='ODBC Driver 17 for SQL Server'):
        self.server = server
        self.database = database
        self.user = user
        self.password = password
        self.driver = driver
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            # Ha nincs megadva felhasználónév és jelszó, akkor Windows hitelesítést használunk
            if self.user and self.password:
                conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};UID={self.user};PWD={self.password}'
            else:
                conn_str = f'DRIVER={self.driver};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;'

            self.conn = pyodbc.connect(conn_str)
            self.cursor = self.conn.cursor()
            print("INFO: Connected to SQL Server")
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Unable to connect to SQL Server: {e}\033[0m")

    def insert_bulk(self, df, table):
        try:
            # Fetch the table from the database
            query = f"SELECT * FROM {table}"
            db_df = self.get_table(table)

            # If the table is empty or None, handle this case
            if db_df is None:
                print(f"INFO: The table {table} does not exist or is empty.")
                return

            # Find the common columns between the DataFrame and the database table
            common_columns = list(set(df.columns).intersection(set(db_df.columns)))

            # If there are common columns, insert data
            if common_columns:
                # Escape column names with square brackets for SQL syntax compatibility
                escaped_columns = [f"[{col}]" for col in common_columns]
                columns = ', '.join(escaped_columns)
                placeholders = ', '.join(['?' for _ in common_columns])
                sql_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

                # Collect values for each row based on the common columns using the DataFrame values
                values = [
                    tuple(row[df.columns.get_loc(col)] for col in common_columns)
                    for row in df.values
                ]

                # Perform the bulk insert
                self.cursor.executemany(sql_query, values)
                self.conn.commit()
                print(f"INFO: Rows from DataFrame inserted into {table} table based on matching columns")
            else:
                print("INFO: No matching columns between DataFrame and database table, skipping insert")

        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to insert DataFrame: {e}\033[0m")

    def insert_row(self, row_data, table):
        try:
            # Példa SQL insert query
            columns = ', '.join(row_data.keys())
            placeholders = ', '.join(['?' for _ in row_data])
            sql_query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            self.cursor.execute(sql_query, tuple(row_data.values()))
            self.conn.commit()
            print("INFO: Row inserted successfully")
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to insert row: {e}\033[0m")

    def update_row(self, keys, updates, table):
        try:
            # Példa SQL update query
            set_clause = ', '.join([f"{k} = ?" for k in updates])
            where_clause = ' AND '.join([f"{k} = ?" for k in keys])
            sql_query = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
            self.cursor.execute(sql_query, tuple(updates.values()) + tuple(keys.values()))
            self.conn.commit()
            print("INFO: Row updated successfully")
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to update row: {e}\033[0m")

    def execute_query(self, query):
        try:
            self.cursor.execute(query)
            results = self.cursor.fetchall()
            print("INFO: Query executed successfully")
            return results
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to execute query: {e}\033[0m")
            return None

    def get_table(self, table):
        try:
            query = f"SELECT * FROM {table}"
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]  # Oszlopnevek kinyerése
            rows = self.cursor.fetchall()
            table_df = pd.DataFrame.from_records(rows, columns=columns)

            print("INFO: Table fetched successfully")
            return table_df
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to fetch table: {e}\033[0m")
            return None

    def query(self, query_string):
        try:
            query = query_string
            self.cursor.execute(query)
            columns = [column[0] for column in self.cursor.description]  # Oszlopnevek kinyerése
            rows = self.cursor.fetchall()
            table_df = pd.DataFrame.from_records(rows, columns=columns)

            # Dátumoszlopok automatikus konvertálása
            for column in columns:
                # Ha a SQL oszlop típusa datetime, konvertáljuk pandas datetime-ra
                if self.cursor.description[columns.index(column)][1] in [pyodbc.SQL_TYPE_TIMESTAMP,
                                                                         pyodbc.SQL_TYPE_DATE]:
                    table_df[column] = pd.to_datetime(table_df[column], errors='coerce')

            print("INFO: Table fetched successfully")
            return table_df
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to fetch table: {e}\033[0m")
            return None

    def delete(self, table, primary_key=None, key_value=None):
        try:
            if primary_key and key_value:
                # Delete rows by primary key
                sql_query = f"DELETE FROM {table} WHERE {primary_key} = ?"
                self.cursor.execute(sql_query, (key_value,))
                self.conn.commit()
                print(f"INFO: Row(s) with {primary_key} = {key_value} deleted successfully")
            else:
                # If no primary key is provided, delete all rows in the table
                sql_query = f"DELETE FROM {table}"
                self.cursor.execute(sql_query)
                self.conn.commit()
                print(f"INFO: All rows in {table} deleted successfully")
        except pyodbc.Error as e:
            print(f"\033[91mERROR: Failed to delete from table: {e}\033[0m")

    def close(self):
        if self.conn:
            self.conn.close()
            print("INFO: Connection to SQL Server closed")
