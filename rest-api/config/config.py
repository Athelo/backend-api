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
    BASE_URL = "https://athelo-api-bki2ktapnq-uc.a.run.app/"
    ZOOM_CLIENT_ID = os.environ.get("ZOOM_CLIENT_ID")
    ZOOM_CLIENT_SECRET = os.environ.get("ZOOM_CLIENT_SECRET")
    REDIS_URL = os.environ.get("REDIS_URL")


class ProductionConfig(CloudConfig):
    LOG_LEVEL = logging.INFO


class StagingConfig(CloudConfig):
    LOG_LEVEL = logging.DEBUG


class LocalConfig(Config):
    DB_NAME = "athelo"
    DB_USER = "athelo"
    DB_PASS = "athelo"
    DB_PORT = 5432
    PORT = os.environ.get("PORT", 8080)
    DB_HOST = os.environ.get("DB_HOST", "db")
    REDIS_HOST = os.environ.get("REDIS_HOST", "redis")
    SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"
    LOG_LEVEL = logging.DEBUG
    DEBUG = True
    SECRET_KEY = "SECRET_KEY"
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5001",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://192.168.0.223:3000",
    ]
    ALLOWED_ADMIN_DOMAINS = ["athelohealth.com", "gmail.com"]
    BASE_URL = "http://localhost:5001"
    ZOOM_CLIENT_ID = "uGg_8H7qSYmioNsz2I83aA"
    ZOOM_CLIENT_SECRET = "97TKYdJIh4QO8eBz1lj2okiDnSxcuw4q"
    REDIS_URL = f"redis://{REDIS_HOST}:6379/0"


class TestingConfig(Config):
    DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
    ALLOWED_ADMIN_DOMAINS = ["athelohealth.com", "gmail.com"]
