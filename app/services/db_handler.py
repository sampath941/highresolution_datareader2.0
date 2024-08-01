import sqlite3
import paramiko
from scp import SCPClient
import os
import pandas as pd
from config import Config



def fetch_data_from_db(filename):
    print(filename)
    if not os.path.exists(filename):
       print(f"Database file does not exist: {filename}")
    else:
        print(f"Database file found: {filename}")
    con = sqlite3.connect(filename)
    cursor = con.cursor()
    cursor.execute("SELECT sqlite_version();")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print("Tables in the database:")
    for table in tables:
        print(table[0])
    version = cursor.fetchone()
    if version is None:
     print("Failed to retrieve SQLite version.")
    else:
     print(f"SQLite version: {version[0]}")
    cursor.execute('SELECT * FROM Event')
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    con.close()
    return pd.DataFrame(rows, columns=columns)
    

def connect_controller(ip_address, username, password):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    tempfilepath = os.path.join(Config.TEMPORARY_FILES_DIR, 'filefromcontroller')
    try:
        ssh.connect(hostname=ip_address, port=22, username=username, password=password)
        with SCPClient(ssh.get_transport()) as scp:
            scp.get('/tmp/asclog.db', tempfilepath)
        return tempfilepath, True, "Successfully connected"
    except Exception as e:
        return False, str(e)
    finally:
        ssh.close()
