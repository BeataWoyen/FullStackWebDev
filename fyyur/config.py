import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

dialect = 'postgresql'
username = ''
password = ''
host = 'localhost'
port = '5432'
database = 'fyyur'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_DATABASE_URI = f'{dialect}://{username}:{password}@{host}:{port}/{database}'
