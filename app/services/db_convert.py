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
    df = fetch_data_from_db(db_path)
    
    if df is None:
        print("No data fetched from the database.")
        return
    

    json_data = load_json_file(eventcodes_path)
    
    # Convert JSON data to DataFrame
    json_df = pd.DataFrame.from_dict(json_data, orient='index').reset_index()
    json_df.rename(columns={'index': 'EventTypeID'}, inplace=True)
    #output_file = 'outputlog'
    #print_dataframe_to_file(json_df, output_file)

    df['EventTypeID'] = df['EventTypeID'].astype(str)
    json_df['EventTypeID'] = json_df['EventTypeID'].astype(str)
    
    # Merge DataFrames on 'EventTypeID'
    merged_df = pd.merge(df, json_df, on='EventTypeID', how='left')
    
    # Select and reorder columns for CSV
    final_df = merged_df[['Timestamp', 'EventTypeID', 'Name', 'Parameter', 'Description']]
    print(final_df)
    return final_df
    