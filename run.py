from app import create_app
from dotenv import load_dotenv
import logging
from flask import Flask

load_dotenv()  # Load environment variables from .env

app = create_app()

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)

