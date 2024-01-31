import os

# Flask env
FLASK_ENV = os.environ.get("FLASK_ENV")
SECRET_KEY = "os.environ.getasdfsdf"

# Redis


# REDIS_URI = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
REDIS_URI = f"redis://default:redispassword@redis:6379/0"


class Config:
    FLASK_ENV = FLASK_ENV
    SECRET_KEY = SECRET_KEY
    REDIS_URI = REDIS_URI
    DEBUG = False
    TESTING = False
    WEBSOCKET_JWT_SECRET_KEY = "secret"
    WEBSOCKET_JWT_ALGORITHM = "HS256"


class DevConfig(Config):
    DEBUG = True


class TestConfig(Config):
    TESTING = True


class ProdConfig(Config):
    pass


config = DevConfig()
