from flask import Flask, Blueprint, render_template, request, redirect, url_for, flash, send_file, get_flashed_messages, session
from ..services.file_operations import save_as_csv, save_as_excel
from ..services.db_handler import fetch_data_from_db, connect_controller
import os
import sys
from app.services import logging_config
from config import Config
import logging
from werkzeug.utils import secure_filename

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
    return render_template('index.html')

@main.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOADS_DIR'], filename)
            file.save(filepath)
            session['uploaded_filepath'] = filepath  # Store filename in session
            flash('File successfully uploaded', 'success')
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
        filepath, success, message = connect_controller(ip_address, username, password)
        if success:
            session['uploaded_filepath'] = filepath
            flash('Successfully connected to the controller and file retrieved', 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('main.index'))
    return render_template('connect.html')

@main.route('/save', methods=['POST'])
def save():
    data_format = request.form.get('data_format')
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
            file_path = save_as_csv(filepath, eventcodes_path, filename)
        else:
            file_path = save_as_excel(filepath, eventcodes_path, filename)

        logging.debug(f"Sending file {file_path} as {filename}")
        if file_path:
            logging.info('main.py - line 84')
            flash('File successfully saved', 'success')
            return send_file(file_path, as_attachment=True, download_name=filename)
    finally:
            flash('File successfully saved', 'success')
            os.remove(filepath)
            session.clear()  # Clean up the uploaded file

    return redirect(url_for('main.index'))


if __name__ == '__main__':
    app.run(debug=True)
