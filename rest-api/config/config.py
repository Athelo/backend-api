import logging
import os

from models.database import getconn


class Config(object):
    TESTING = False
    PORT = os.environ.get("PORT")
    WEBSOCKET_JWT_ALGORITHM = os.environ.get("WEBSOCKET_JWT_ALGORITHM", "HS256")
    WEBSOCKET_JWT_SECRET_KEY = os.environ.get("WEBSOCKET_JWT_SECRET_KEY", "secret")


class CloudConfig(Config):
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://"
    SQLALCHEMY_ENGINE_OPTIONS = {"creator": getconn}
    DB_NAME = os.environ.get("DB_NAME", None)
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    PROJECT = os.environ.get("PROJECT")
    REGION = os.environ.get("REGION")
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")
    DEBUG = False
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALLOWED_ADMIN_DOMAINS = ["athelohealth.com"]


class ProductionConfig(CloudConfig):
    LOG_LEVEL = logging.INFO


class StagingConfig(CloudConfig):
    LOG_LEVEL = logging.DEBUG


class LocalConfig(Config):
    DB_NAME = "athelo"
    DB_USER = "athelo"
    DB_PASS = "athelo"
    DB_PORT = 5432
    PORT = 8000
    SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@db/{DB_NAME}"
    LOG_LEVEL = logging.DEBUG
    DEBUG = True
    SECRET_KEY = "SECRET_KEY"
    CORS_ALLOWED_ORIGINS = [
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://192.168.0.223:3000",
    ]
    ALLOWED_ADMIN_DOMAINS = ["athelohealth.com", "gmail.com"]


class TestingConfig(Config):
    DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    ALLOWED_ADMIN_DOMAINS = ["athelohealth.com", "gmail.com"]
