import os
from google.cloud.sql.connector import Connector, IPTypes
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

# initialize Python Connector object
connector = Connector()


# Python Connector database connection function
def getconn():
    project = current_app.config["PROJECT"]
    region = current_app.config["REGION"]
    instance_connection_name = ["INSTANCE_CONNECTION_NAME"]
    conn = connector.connect(
        f"{project}:{region}:{instance_connection_name}",  # Cloud SQL Instance Connection Name
        "pg8000",
        user=current_app.config.get("DB_USER"),
        password=current_app.config.get("DB_PASS"),
        db=current_app.config.get("DB_NAME"),
        ip_type=IPTypes.PRIVATE,  # IPTypes.PRIVATE for private IP
    )
    return conn


# initialize the app with the extension
db = SQLAlchemy()
__all__ = ["vote", "base"]
