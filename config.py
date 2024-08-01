import os

# Define the base directory for the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define other configurations
class Config:
    TEMPORARY_FILES_DIR = os.path.join(BASE_DIR, 'temporary_files')
    BASE_DIR = BASE_DIR
    UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
