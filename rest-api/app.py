from __future__ import annotations

import os

from api import blueprints
from config.logging import setup_logging
from flask import Flask
from flask_marshmallow import Marshmallow
from models.base import Base
from models.database import db
from models.saved_content import SavedContent
from models.symptom import Symptom
from models.user_profile import UserProfile
from models.user_symptom import UserSymptom
from models.user_feeling import UserFeeling


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
        Base.metadata.create_all(bind=db.engine)

        for blueprint in blueprints:
            app.register_blueprint(blueprint=blueprint)

    ma = Marshmallow(app)
    app.logger.info("Running app!")
    return app
