import pandas as pd
from app.services.db_handler import fetch_data_from_db
import os
import json
from app.services import logging_config
import logging


def load_json_file(eventcodes_path):
    logging.info('You are in debug message')
    with open(eventcodes_path, 'r') as f:
        return json.load(f)
    
def combine_and_convert_df(db_path, eventcodes_path):
    # Fetch data from the database
    dataframes = fetch_data_from_db(db_path)
    
    if dataframes is None or not dataframes:
        print("No data fetched from the database.")
        return

    json_data = load_json_file(eventcodes_path)
    
    # Convert JSON data to DataFrame
    json_df = pd.DataFrame.from_dict(json_data, orient='index').reset_index()
    json_df.rename(columns={'index': 'EventTypeID'}, inplace=True)

    final_dfs = {}

    for table_name, df in dataframes.items():
        if 'EventTypeID' in df.columns:
            df['EventTypeID'] = df['EventTypeID'].astype(str)
            json_df['EventTypeID'] = json_df['EventTypeID'].astype(str)
        
            # Merge DataFrames on 'EventTypeID'
            merged_df = pd.merge(df, json_df, on='EventTypeID', how='left')
        
            # Select and reorder columns for CSV if the required columns are present
            columns_to_select = ['Timestamp', 'EventTypeID', 'Name', 'Parameter', 'Description']
            if all(col in merged_df.columns for col in columns_to_select):
                final_df = merged_df[columns_to_select]
                final_dfs[table_name] = final_df
                print(f"Data from table {table_name}:")
                print(final_df)
            else:
                print(f"Required columns not found in table {table_name}.")
        else:
            print(f"'EventTypeID' column not found in table {table_name}.")

    return final_dfs
