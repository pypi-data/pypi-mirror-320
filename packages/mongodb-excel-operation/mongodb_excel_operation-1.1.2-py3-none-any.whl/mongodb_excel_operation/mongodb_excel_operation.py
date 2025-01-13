# mongodb_excel_utils.py

import pandas as pd
import pymongo
myclient = pymongo.MongoClient('mongodb://localhost:27017/')


def read_file(path, file_ext, sheet_index):
    """
    Reads a file (CSV or Excel) and returns a DataFrame with all columns as strings.
    """
    try:
        if file_ext == 'csv':
            df_column = pd.read_csv(path, nrows=0).columns
        else:
            df_column = pd.read_excel(path, sheet_name=sheet_index, nrows=0).columns
        converter = {col: str for col in df_column}
        if file_ext == 'csv':
            df = pd.read_csv(path, converters=converter)
        else:
            df = pd.read_excel(path, sheet_name=sheet_index, converters=converter)
        df.reset_index(drop=True, inplace=True)
        df.fillna('', inplace=True)
        print("File successfully read.")
        return df
    except Exception as e:
        print(f"Error reading file: {e}")
        return pd.DataFrame()

def import_excel_to_table(db, file_name, table_name):
    """
    Imports data from an Excel file into a MongoDB collection.
    """
    try:
        data = read_file(path=file_name,file_ext='.xlsx', sheet_index=0)
        if data.empty:
            print(f"The Excel file '{file_name}' is empty.")
            return
        records = data.to_dict(orient='records')
        connection = myclient[db]
        result = connection[table_name].insert_many(records)
        print(f"Successfully imported {len(result.inserted_ids)} records into the collection '{table_name}'.")
    except Exception as e:
        print(f"An error occurred during import: {e}")

def export_as_excel_from_table(db, table_name):
    """
    Exports data from a MongoDB collection to an Excel file.
    """
    try:
        connection = myclient[db]
        data = pd.DataFrame(connection[table_name].find({}, {'_id': 0}))
        if data.empty:
            print(f"No data found in the collection '{table_name}'.")
            return
        output_file = f"{table_name}.xlsx"
        data.to_excel(output_file, index=False)
        print(f"Data successfully exported to '{output_file}'.")
    except Exception as e:
        print(f"An error occurred while exporting data: {e}")



def table_indexing(db:str, table_name:str):
    """
    Drops and recreates non-unique indexes on all fields in a MongoDB collection.
    """
    try:
        mydb = myclient[db]
        sample_data = list(mydb[table_name].find({}, {'_id': False}).limit(10))
        if not sample_data:
            print(f"No data found in the '{table_name}' table.")
            return 'No data'
        col_list = list(sample_data[0].keys())
        print("Columns detected:", col_list)
        for field in col_list:
            try:
                mydb[table_name].drop_index([(field, 1)])
                print(f"Index on '{field}' dropped successfully.")
            except:
                print(f"No existing index to drop on '{field}'.")
            try:
                index_result = mydb[table_name].create_index([(field, 1)], unique=False)
                print(f"Index created on '{field}': {index_result}")
            except Exception as e:
                print(f"Failed to create index on '{field}': {e}")
        return 'Indexing complete'
    except Exception as e:
        print(f"Error in table indexing: {e}")
        return 'Error'
