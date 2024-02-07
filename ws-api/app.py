import eventlet
eventlet.monkey_patch()

from flask import Flask
from flask_cors import CORS
from config import config
from websocket import socketio
from cache import cache


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    register_extensions(app)
    if config.REDIS_URL:
        cache.init_app(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": config.REDIS_URL})
    else:
        cache.init_app(app, {"CACHE_TYPE": "SimpleCache"})

    return app


def register_extensions(app):
    socketio.init_app(app, logger=True, engineio_logger=True, cors_allowed_origins="*", async_mode="eventlet", message_queue=config.REDIS_URL)


app = create_app()
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
