from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlite3 import Connection as SQLite3Connection
from .libs.exceptions import FyleError

app = Flask(__name__) # Initializes the Flask app

# sets up the database URI to use SQLite,
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./store.sqlite3'
# if True, SQLAlchemy will log all the raw SQL statements
app.config['SQLALCHEMY_ECHO'] = False
# Disables tracking 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# sets test client to simulate HTTP requests for testing, allows to call endpoints during testing without running the server
app.test_client()


# this is to enforce fk (not done by default in sqlite3)
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


# @app.errorhandler(FyleError)
# def handle_fyle_error(error):
#     response = jsonify(error.to_dict()) 
#     response.status_code = error.status_code
#     return response