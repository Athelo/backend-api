import os
from google.cloud.sql.connector import Connector, IPTypes
from flask_sqlalchemy import SQLAlchemy
from flask import current_app

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


if os.environ.get("ENVIRONMENT", None) == "local":
    current_app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = f"postgresql+pg8000://{db_user}:{db_pass}@db/{db_name}"
else:
    current_app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"
    current_app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"creator": getconn}

# initialize the app with the extension
db = SQLAlchemy()
__all__ = ["vote", "base"]
