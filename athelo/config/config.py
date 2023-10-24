import logging
from models.database import getconn
import os


class Config(object):
    TESTING = False


class CloudConfig(object):
    SQLALCHEMY_DATABASE_URI = "postgresql+pg8000://"
    SQLALCHEMY_ENGINE_OPTIONS = {"creator": getconn}
    DB_NAME = os.environ.get("DB_NAME", None)
    DB_USER = os.environ.get("DB_USER")
    DB_PASS = os.environ.get("DB_PASS")
    PROJECT = os.environ.get("PROJECT")
    region = os.environ.get("REGION")
    INSTANCE_CONNECTION_NAME = os.environ.get("INSTANCE_CONNECTION_NAME")


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


class TestingConfig(Config):
    DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
