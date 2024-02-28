import eventlet

eventlet.monkey_patch()

from cache import cache
from config import config
from flask import Flask
from flask_cors import CORS
from websocket import socketio


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={r"/*": {"origins": "*"}})

    register_extensions(app)
    if config.REDIS_URL:
        cache.init_app(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": config.REDIS_URL})
    else:
        cache.init_app(app, {"CACHE_TYPE": "SimpleCache"})

    return app


def register_extensions(app):
    socketio.init_app(app)


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=config.PORT, debug=config.DEBUG)
