from flask import Flask
from flask_cors import CORS

# Configuration
from flask_app.config import config

# Extensions
from flask_app.websocket import socketio

from flask_app.cache import cache


def create_app():
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['DEBUG'] = True
    CORS(app, resources={r"/*": {"origins": "*"}})

    register_extensions(app)
    cache.init_app(app, {"CACHE_TYPE": "SimpleCache"})
    # cache.init_app(app, {"CACHE_TYPE": "RedisCache", "CACHE_REDIS_URL": config.REDIS_URI})

    return app


def register_extensions(app):
    socketio.init_app(app)


app = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5002, debug=True)