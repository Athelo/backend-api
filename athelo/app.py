from __future__ import annotations

import logging
from flask import Flask, render_template, request, Response

from models import db

from views.vote import vote_endpoints
from views.main import main_endpoints

# from flask_migrate import Migrate


app = Flask(__name__)
# configure Flask-SQLAlchemy to use Python Connector

db.init_app(app)
# migrate = Migrate(app, db)

app.register_blueprint(vote_endpoints)
app.register_blueprint(main_endpoints)

logger = logging.getLogger()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
