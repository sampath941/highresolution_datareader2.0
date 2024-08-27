import sqlite3
import paramiko
from scp import SCPClient
import os
import pandas as pd
from config import Config
from flask import flash



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
    

def connect_controller(ip_address, username, password, file_source):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    os.makedirs(Config.TEMPORARY_FILES_DIR, exist_ok=True)
    tempfilepath = os.path.join(Config.TEMPORARY_FILES_DIR, 'filefromcontroller')
    source_paths = {
        'active': '/tmp/asclog.db',
        'usb': '/media/usb/asclog.db',
        'sd_card': '/media/sdcard/asclog.db'
    }
    source_path = source_paths.get(file_source)
    try:
        ssh.connect(hostname=ip_address, port=22, username=username, password=password)
        flash('Connection to Controller is Successful', 'success')
        try:
            with SCPClient(ssh.get_transport()) as scp:
                scp.get(source_path, tempfilepath)
            return tempfilepath, True, "Successfully connected and file transferred"
        except Exception as scp_error:
            return None, False, f"Failed to transfer file: {scp_error}"
    except Exception as ssh_error:
        flash ('Cannot establish connection with controller', 'error')
        return None, False, f"SSH connection failed: {ssh_error}"
    finally:
        ssh.close()
