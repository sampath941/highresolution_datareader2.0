import sqlite3
import paramiko
from scp import SCPClient
import os
import pandas as pd
from config import Config



def fetch_data_from_db(filename):
    if not os.path.exists(filename):
        print(f"Database file does not exist: {filename}")
        return None

    con = sqlite3.connect(filename)
    cursor = con.cursor()

    # Fetch all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    dataframes = {}

    # Loop through each table and fetch data
    for table in tables:
        table_name = table[0]
        print(f"Fetching data from table: {table_name}")

        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [description[0] for description in cursor.description]

        # Store the DataFrame in a dictionary with the table name as the key
        dataframes[table_name] = pd.DataFrame(rows, columns=columns)

    con.close()
    return dataframes
    

def connect_controller(ip_address, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    tempfilepath = os.path.join(Config.TEMPORARY_FILES_DIR, 'filefromcontroller')
    try:
        ssh.connect(hostname=ip_address, port=22, username=username, password=password)
        try:
            with SCPClient(ssh.get_transport()) as scp:
                scp.get('/tmp/asclog.db', tempfilepath)
            return tempfilepath, True, "Successfully connected and file transferred"
        except Exception as scp_error:
            return None, False, f"Failed to transfer file: {scp_error}"
    except Exception as ssh_error:
        return None, False, f"SSH connection failed: {ssh_error}"
    finally:
        ssh.close()
