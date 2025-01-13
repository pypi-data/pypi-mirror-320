# MongoDB Excel Utilities

This script, `mongodb_excel_operation.py`, provides utility functions to manage data flow between MongoDB and Excel/CSV files. It simplifies operations like importing data into MongoDB collections, exporting data to Excel files, and managing indexes on MongoDB collections.

## Features

1. **Read File**
   - Reads data from CSV or Excel files into a Pandas DataFrame, ensuring all columns are treated as strings.
   - Handles missing values gracefully.

2. **Import Data from Excel to MongoDB**
   - Imports data from an Excel file into a specified MongoDB collection.
   - Converts the data to a record format before storing it in the database.

3. **Export Data from MongoDB to Excel**
   - Exports data from a MongoDB collection to an Excel file.
   - Ignores MongoDB's `_id` field during the export.

4. **MongoDB Collection Indexing**
   - Drops existing indexes on a collection's fields and recreates non-unique indexes for all fields.
   - Provides feedback on index creation and potential issues.

## Requirements

- Python 3.7+
- Libraries: `pandas`, `pymongo`
- A running MongoDB instance accessible at `mongodb://localhost:27017/`.

## Installation

pip install mongodb-excel-operation


## Example

1.Read File
>>> df = read_file(path="path/to/file.csv", file_ext="csv", sheet_index=0)


2. Importing Excel Data into MongoDB
>>> import_excel_to_table(db="my_database", file_name="data.xlsx", table_name="my_collection")

3. Exporting Data from MongoDB to Excel
>>> export_as_excel_from_table(db="my_database", table_name="my_collection")

4. Indexing a MongoDB Collection
>>> table_indexing(db="my_database", table_name="my_collection")



