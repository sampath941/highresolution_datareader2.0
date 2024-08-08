from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, send_file, get_flashed_messages, session, jsonify
from ..services.file_operations import save_as_csv, save_as_excel
from ..services.db_handler import fetch_data_from_db, connect_controller
import os
import sys
from app.services import logging_config
from config import Config
import logging
import zipfile
from werkzeug.utils import secure_filename
import sqlite3
import shutil

# Add 'utils' directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

# Create a blueprint for the main part of the application
main = Blueprint('main', __name__)
app = Flask(__name__)
app.config.from_object(Config)
logging_config.configure_logging()
app.secret_key = 'your_secret_key'  # Set a secret key for session management

logging.info('I am in main.py file')
print(Config.BASE_DIR)

eventcodes_path = os.path.join(Config.BASE_DIR, 'event_codes.json')

@main.route('/')
def index():
    export_enabled = session.get('export_enabled', False)
    return render_template('index.html', export_enabled=export_enabled) 

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            save_upload_dir = Config.UPLOADS_DIR
            os.makedirs(save_upload_dir, exist_ok=True)
            filepath = os.path.join(save_upload_dir, filename)
            file.save(filepath)
            session['uploaded_filepath'] = filepath  # Store filename in session
            session['export_enabled'] = True
            flash('File successfully uploaded. Please give any filename and export it to your PC', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('No file selected', 'danger')
    return render_template('upload.html')

@main.route('/connect', methods=['GET', 'POST'])
def connect():
    if request.method == 'POST':
        ip_address = request.form['ip_address']
        username = request.form['username']
        password = request.form['password']
        file_source = request.form['file_source']
        filepath, success, message = connect_controller(ip_address, username, password, file_source)
        if success:
            session['uploaded_filepath'] = filepath
            session['export_enabled'] = True
            flash('File successfully retrieved. Please give desired filename and export it to your PC ', 'success')
#            return jsonify({'success': True, 'filepath': filepath, 'message': message})
        else:
            flash('Cannot get the file, please check if the file exists in the correct folder. Please refresh the page and try again', 'error')
            logging.info('you did not get the file')
        return redirect(url_for('main.index'))
    return render_template('connect.html')

@main.route('/save', methods=['POST'])
def save():
    data_format = request.form.get('data_format')
    logging.info('Data Format selected is %s', data_format)
    filename = request.form.get('filename')
    filepath = session.get('uploaded_filepath')
    logging.debug(' I am in Save Function, Line 65')

    if not filepath:
        logging.error('No file uploaded')
        flash('No file uploaded', 'danger')
        return redirect(url_for('main.index'))
    
    extension = '.csv' if data_format == 'csv' else '.xlsx'
    if not filename.endswith(extension):
        filename += extension

    try:
        if data_format == 'csv':
            file_paths = save_as_csv(filepath, eventcodes_path, filename)
            if file_paths:
                zip_filename = f"{os.path.splitext(filename)[0]}.zip"
                zip_filepath = os.path.join(Config.TEMPORARY_FILES_DIR, zip_filename)
                with zipfile.ZipFile(zip_filepath, 'w') as zipf:
                    for file in file_paths:
                        zipf.write(file, os.path.basename(file))
                        os.remove(file)  # Clean up individual CSV files after zipping
                logging.debug(f"Sending zip file {zip_filepath} as {zip_filename}")
                flash('File successfully saved', 'success')
                response = send_file(zip_filepath, as_attachment=True, download_name=zip_filename)
                response.call_on_close(lambda: cleanup(zip_filepath))
                return response
        else:
            file_path = save_as_excel(filepath, eventcodes_path, filename)
            logging.debug(f"Sending file {file_path} as {filename}")
            if file_path:
                logging.info(filename)
                logging.info('main.py - line 84')
                response = send_file(file_path, as_attachment=True, download_name=filename)
                response.call_on_close(lambda: cleanup(file_path))
                return response
    except sqlite3.DatabaseError as e:
        logging.error(f"Database error: {e}")
        flash('Failed to process the database file. The database might be corrupted.', 'danger')
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        flash('An unexpected error occurred.', 'danger')

    finally:
        try:
            os.remove(filepath)
        except PermissionError:
            logging.error(f"Permission error: Could not remove file {filepath}")
        except Exception as e:
            logging.error(f"Error removing file {filepath}: {e}")
        session.clear()
    return redirect(url_for('main.index'))
        
        # Delete all temporary files in the temporary directory
def cleanup(file_path):
    # Delete the file
    try:
        os.remove(file_path)
        logging.info(f"Temporary file {file_path} removed.")
    except Exception as e:
        logging.error(f"Error removing temporary file {file_path}: {e}")
    # Delete all temporary files in the temporary directory
    temp_dir = Config.TEMPORARY_FILES_DIR
    if os.path.exists(temp_dir):
        try:
            shutil.rmtree(temp_dir)
            logging.info(f"Temporary directory {temp_dir} removed.")
        except Exception as e:
            logging.error(f"Error removing temporary directory {temp_dir}: {e}")


if __name__ == '__main__':
    app.run(debug=True)
