import pandas as pd
from app.services.db_convert import alldataconvert  # Replace 'your_module' with the actual name of your module where 'alldataconvert' is defined
from app.services.db_handler import fetch_data_from_db
import os
import sqlite3
import json

print('Hi????')
# Define the path to your test directory
# test_directory = 'app'

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
db_path = os.path.join(project_root, 'asclog.db')
print(db_path)

def load_json_file(json_file):
    with open(json_file, 'r') as f:
        return json.load(f)
    
    
def combine_and_convert_df(db_path, json_file, output_csv):
    # Fetch data from the database
    df = fetch_data_from_db(db_path)
    
    if df is None:
        print("No data fetched from the database.")
        return
    

    json_data = load_json_file(json_file)
    
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
    # Export to CSV
    final_df.to_csv(output_csv, index=False)
    print(f"Data exported to CSV at {output_csv}")

# Usage
json_file = 'event_codes.json'
output_csv = 'merged_data.csv'
combine_and_convert_df(db_path, json_file, output_csv)


    ###
    # def print_dataframe_to_file(df, output_file):
    # # Set pandas options to display all columns and rows
    #     pd.set_option('display.max_columns', None)  # Show all columns
    #     pd.set_option('display.max_rows', None)     # Show all rows
    #     pd.set_option('display.max_colwidth', None) # Show full column width
    
    # # Redirect output to a file
    #     with open(output_file, 'w') as file:
    #     # Write DataFrame info
    #         file.write("DataFrame Info:\n")
    #         file.write(f"Shape: {df.shape}\n")
    #         file.write(f"Columns: {', '.join(df.columns)}\n\n")
        
    #     # Write DataFrame content
    #         file.write("DataFrame Content:\n")
    #         file.write(df.to_string(index=False)) 

            ###
    # Load JSON data

# import os


# db_path = os.path.join(os.path.dirname(__file__), 'asclog.db')

# if not os.path.exists(db_path):
#     print(f"Database file does not exist: {db_path}")
# else:
#     print(f"Database file found: {db_path}")

# con = sqlite3.connect(db_path)
# cursor = con.cursor()
# cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
# tables = cursor.fetchall()
# print("Tables in the database:")
# for table in tables:
#     print(table[0])
# cursor.execute("SELECT sqlite_version();")
# version = cursor.fetchone()
# if version is None:
#     print("Failed to retrieve SQLite version.")
# else:
#     print(f"SQLite version: {version[0]}")
# cursor.execute('SELECT * FROM Event')
# rows = cursor.fetchall()
# print (rows)
# con.close()



# Load and print the contents of the output CSV file for inspection
#df = pd.read_csv(output_file)
#print(df)