from __future__ import annotations

import os

from flask_cors import CORS
from cache import cache
from api import blueprints, handle_database_error, handle_unauthorized
from auth.exceptions import UnauthorizedException
from config.logging import setup_logging
from flask import Flask
from flask_marshmallow import Marshmallow
from models.database import db, migrate
from services.cloud_storage import CloudStorageService
from services.opentok import OpenTokClient
from sqlalchemy.exc import DatabaseError, IntegrityError


def set_config(app: Flask):
    environment = os.environ.get("ENVIRONMENT", "")
    config_module = "config.config."
    match environment.lower():
        case "test":
            config_module = f"{config_module}LocalConfig"
        case "local":
            config_module = f"{config_module}LocalConfig"
        case "production":
            config_module = f"{config_module}ProductionConfig"
        case "staging" | _:
            config_module = f"{config_module}StagingConfig"

    app.config.from_object(config_module)


def create_app() -> Flask:
    app = Flask(__name__)
    set_config(app)
    setup_logging(app)
    cache.init_app(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": app.config.get("REDIS_URL")})

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)

        for blueprint in blueprints:
            app.register_blueprint(blueprint=blueprint)

        app.register_error_handler(DatabaseError, handle_database_error)
        app.register_error_handler(IntegrityError, handle_database_error)
        app.register_error_handler(UnauthorizedException, handle_unauthorized)

        OpenTokClient.init_app(app)
        CloudStorageService.init_app(app)

    ma = Marshmallow(app)  # noqa: F841
    app.logger.info("Running app!")
    return app


app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
