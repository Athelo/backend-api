import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "SECRET_KEY")
    REDIS_URL = os.environ.get("REDIS_URL")
    DEBUG = False
    TESTING = False
    WEBSOCKET_JWT_ALGORITHM = os.environ.get("WEBSOCKET_JWT_ALGORITHM", "HS256")
    WEBSOCKET_JWT_SECRET_KEY = os.environ.get("WEBSOCKET_JWT_SECRET_KEY", "secret")
    REST_API_SERVER_URL = os.environ.get("REST_API_SERVER_URL", "http://rest-api:8080")


class StagingConfig(Config):
    DEBUG = True


class ProdConfig(Config):
    pass


if os.environ.get("ENVIRONMENT") == "prod":
    config = ProdConfig()
elif os.environ.get("ENVIRONMENT") == "staging":
    config = StagingConfig()
else:
    config = Config()
