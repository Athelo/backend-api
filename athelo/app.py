from __future__ import annotations

from flask import Flask
from config.logging import setup_logging
from flask_marshmallow import Marshmallow


def create_app() -> Flask:
    app = Flask(__name__)
    setup_logging(app)

    with app.app_context():
        from models import db
        from models.base import Base
        from models.symptom import Symptom
        from models.vote import Vote
        from models.user_profile import UserProfile
        from models.user_symptom import UserSymptom

        db.init_app(app)
        Base.metadata.create_all(bind=db.engine)

        from api import blueprints

        for blueprint in blueprints:
            app.register_blueprint(blueprint=blueprint)

    ma = Marshmallow(app)
    app.logger.info("Running app!")
    return app
