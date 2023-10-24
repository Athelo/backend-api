from __future__ import annotations

from typing import Optional
from flask import Flask, render_template, request, Response
from config.logging import setup_logging


def create_app() -> Flask:
    app = Flask(__name__)
    setup_logging(app)
    with app.app_context():
        from models import db

        db.init_app(app)
        db.create_all()

        from api import blueprints

        for blueprint in blueprints:
            app.register_blueprint(blueprint=blueprint)
    app.logger.info("Running app!")
    return app
