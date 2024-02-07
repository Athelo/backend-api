import logging
import os

from models.database import getconn


class Config(object):
    TESTING = False
    PORT = os.environ.get("PORT")
    MAX_CONTENT_LENGTH = 1024 * 1024
    UPLOAD_EXTENSIONS = [".jpg", ".png", ".gif"]


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
    BASE_URL = "https://athelo-api-bki2ktapnq-uc.a.run.app/"
    ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
    ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
    VONAGE_API_KEY = os.environ.get("VONAGE_API_KEY")
    VONAGE_API_SECRET = os.environ.get("VONAGE_API_SECRET")
    STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET")


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
    BASE_URL = "http://localhost:5001"
    ZOOM_CLIENT_ID = "uGg_8H7qSYmioNsz2I83aA"
    ZOOM_CLIENT_SECRET = "97TKYdJIh4QO8eBz1lj2okiDnSxcuw4q"
    VONAGE_API_KEY = "47853731"
    VONAGE_API_SECRET = "25851f9cb85dba8e206be42841da93c73832228a"
    STORAGE_BUCKET = "athelo-ad72bbe5-6171-49d6-b116-9a8236c4213a"


class TestConfig(LocalConfig):
    SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{LocalConfig.DB_USER}:{LocalConfig.DB_PASS}@db/{LocalConfig.DB_NAME}test"
    TESTING = True
    VONAGE_API_KEY = "1"
    VONAGE_API_SECRET = "key"
