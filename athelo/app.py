from __future__ import annotations

import logging
import os
from flask import Flask, render_template, request, Response
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from google.cloud.sql.connector import Connector, IPTypes
from views.vote import vote_endpoints
from views.main import main_endpoints

# from flask_migrate import Migrate


# initialize Python Connector object
connector = Connector()


db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]


# Python Connector database connection function
def getconn():
    instance_connection_name = os.environ["INSTANCE_CONNECTION_NAME"]
    conn = connector.connect(
        f"test-deploy-402816:us-central1:{instance_connection_name}",  # Cloud SQL Instance Connection Name
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        ip_type=IPTypes.PRIVATE,  # IPTypes.PRIVATE for private IP
    )
    return conn


app = Flask(__name__)
# configure Flask-SQLAlchemy to use Python Connector
if os.environ["ENVIRONMENT"] == "local":
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql+pg8000://{db_user}:{db_pass}@db/{db_name}"
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"creator": getconn}

# initialize the app with the extension
db = SQLAlchemy()
db.init_app(app)
# migrate = Migrate(app, db)

app.register_blueprint(vote_endpoints)
app.register_blueprint(main_endpoints)

logger = logging.getLogger()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
