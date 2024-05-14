import os
from dotenv import dotenv_values
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
# IMPLEMENT DATABASE URL
config = dotenv_values(".env")
SQLALCHEMY_DATABASE_URI = f"postgresql://{config['DB_USER']}:{config['DB_PASSWORD']}@{config['DB_HOST']}/{config['DB_NAME']}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True