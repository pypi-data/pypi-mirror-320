# BaseConnect

## Introduction

The BaseConnect library simplifies database operations for SQL Server by providing an easy-to-use Python interface. 
It abstracts repetitive tasks like connecting to the database, executing queries, and fetching data into pandas 
DataFrames. This package is built using pyodbc and pandas.

## Installation

To use BaseConnect, ensure you have the following dependencies installed:

pyodbc: For database connection
pandas: For data manipulation
Install the dependencies using pip:

```bash  
pip install pyodbc pandas
```
Include the BaseConnect package in your Python project structure.

## Database Class

The Database class is the core component of the BaseConnect package. 
It provides methods for connecting to SQL Server, executing queries, and managing data.

**Initialization**
```bash
from baseconnect import Database
```
```bash
db = Database(
    server="server_name",
    database="database_name",
    user="username",                           # Optional, for SQL authentication
    password="password",                       # Optional, for SQL authentication
    driver="ODBC Driver 17 for SQL Server"     # Default driver
)
```

* **server (str)**: The SQL Server hostname or IP address.
* **database (str)**: The database name to connect to.
* **user (str)**: (Optional) The username for SQL authentication. Leave empty for Windows Authentication.
* **password (str)**: (Optional) The password for SQL authentication.
* **driver (str)**: (Optional) The ODBC driver to use. Defaults to "ODBC Driver 17 for SQL Server."

## Methods
___

### 1. connect()

Establishes a connection to the SQL Server database.

```bash
db.connect()
```
_Output: Prints a success or error message._

___

### 2. close()

Closes the database connection.
```bash
db.close()
```
_Output: Prints a confirmation message when the connection is closed._
___

### 3. insert_row(row_data, table)

Inserts a new row into the specified table.
```bash
row_data = {"column1": value1, "column2": value2, ...}
table = "table_name"
db.insert_row(row_data, table)
```
Parameters:

**row_data (dict)**: Dictionary where keys are column names and 
values are the respective data.

**table (str)**: The table name where the row should be inserted.

_Output: Prints a success or error message._
___

### 4. update_row(keys, updates, table)

Updates a row in the specified table.
```bash
keys = {"primary_key_column": value}
updates = {"column_to_update": new_value, ...}
table = "table_name"
db.update_row(keys, updates, table)
```


Parameters:

**keys (dict)**: Dictionary of key-value pairs used in the WHERE clause.

**updates (dict)**: Dictionary of column-value pairs to update.

**table (str)**: The table name where the update should occur.

_Output: Prints a success or error message._
___

### 5. execute_query(query)

Executes a custom SQL query.
```bash
query = "SELECT * FROM table_name WHERE column_name = 'value'"
results = db.execute_query(query)
```
Parameters:

**query (str)**: The SQL query to execute.

_Returns: List of tuples containing query results (if any)._
___

### 6. get_table(table)

Fetches all rows from the specified table and returns them as a pandas DataFrame.
```bash
table = "table_name"
table_df = db.get_table(table)
```
Parameters:

**table (str)**: The table name to fetch.

_Returns: A pandas DataFrame containing all rows from the table._
___

### 7. query(query_string)

Executes a custom SQL query and returns the results as a pandas DataFrame.
```bash
query_string = "SELECT * FROM table_name WHERE column_name = 'value'"
query_df = db.query(query_string)
```
Parameters:

**query_string (str)**: The SQL query to execute.

_Returns: A pandas DataFrame containing the query results._
___
## Best Practices

Always close the database connection using close() to release resources.
Handle exceptions for invalid queries or data input to prevent SQL injection.
Use environment variables to store sensitive information like database credentials.

## Error Handling

The Database class includes basic error handling, which prints error messages 
for connection failures or query errors.

## Conclusion

BaseConnect is a flexible and efficient library for managing SQL Server databases in Python. 
With its intuitive interface and pandas integration, it is ideal for applications requiring data manipulation 
and analytics.

