from __future__ import annotations

import eventlet
eventlet.monkey_patch(socket=True)


import os

from flask_cors import CORS

from api import blueprints
from cache import cache
from config.logging import setup_logging
from flask import Flask
from flask_marshmallow import Marshmallow
from models.database import db, migrate
from websocket.socketio import setup_socketio


def set_config(app: Flask):
    environment = os.environ.get("ENVIRONMENT", "")
    config_module = "config.config."
    match environment.lower():
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

    with app.app_context():
        db.init_app(app)
        migrate.init_app(app, db)

        for blueprint in blueprints:
            app.register_blueprint(blueprint=blueprint)

    ma = Marshmallow(app)
    app.logger.info("Running app!")
    return app


app = create_app()
CORS(app, resources={r"/*":{"origins":"*"}})
cache.init_app(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": app.config.get("REDIS_URL", None)})
socket_io = setup_socketio(app)


if __name__ == "__main__":
    socket_io.run(app, host="0.0.0.0", port=app.config.get("PORT"), debug=True)
