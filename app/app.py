from __future__ import annotations

import datetime
import logging
import os

from flask import Flask, render_template, request, Response

import sqlalchemy
from sqlalchemy.orm import DeclarativeBase

from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, func
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from google.cloud.sql.connector import Connector, IPTypes


# initialize Python Connector object
connector = Connector()


db_user = os.environ["DB_USER"]
db_pass = os.environ["DB_PASS"]
db_name = os.environ["DB_NAME"]


# Python Connector database connection function
def getconn():
    conn = connector.connect(
        "test-deploy-402816:us-central1:quickstart-instance",  # Cloud SQL Instance Connection Name
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        ip_type=IPTypes.PRIVATE,  # IPTypes.PRIVATE for private IP
    )
    return conn


app = Flask(__name__)

# configure Flask-SQLAlchemy to use Python Connector
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql+pg8000://"
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"creator": getconn}

# initialize the app with the extension
db = SQLAlchemy()
db.init_app(app)

logger = logging.getLogger()


class Base(DeclarativeBase):
    pass


class Vote(Base):
    __tablename__ = "votes"

    vote_id: Mapped[int] = mapped_column(primary_key=True)
    time_cast: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    candidate: Mapped[str] = mapped_column(nullable=False)


@app.route("/votes_model", methods=["GET"])
def render_index_model() -> str:
    """Serves the index page of the app."""
    votes = []
    recent_votes = db.session.scalars(
        db.select(Vote).order_by(Vote.time_cast.desc()).limit(5)
    ).all()
    for vote in recent_votes:
        votes.append({"candidate": vote.candidate, "time_cast": vote.time_cast})
    tab_count = db.session.scalar(
        db.select(func.count().filter(Vote.candidate == "TABS"))
    )
    space_count = db.session.scalar(
        db.select(func.count().filter(Vote.candidate == "SPACES"))
    )
    context = {
        "space_count": space_count,
        "recent_votes": votes,
        "tab_count": tab_count,
    }
    return render_template("index.html", **context)


@app.route("/votes_model", methods=["POST"])
def cast_vote_model() -> Response:
    """Processes a single vote from user."""
    team = request.form["team"]
    if team != "TABS" and team != "SPACES":
        logger.warning(f"Received invalid 'team' property: '{team}'")
        return Response(
            response="Invalid team specified. Should be one of 'TABS' or 'SPACES'",
            status=400,
        )
    vote = Vote(candidate=team)
    db.session.add(vote)
    db.session.commit()
    return Response(
        status=200,
        response=f"Vote successfully cast for '{vote.candidate}' at time {vote.time_cast}!",
    )


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


# get_index_context gets data required for rendering HTML application
def get_index_context(db: sqlalchemy.engine.base.Engine) -> dict:
    """Retrieves data from the database about the votes.

    Args:
        db: Connection to the database.
    Returns:
        A dictionary containing information about votes.
    """
    votes = []
    logger.info("get index context")
    with db.connect() as conn:
        # Execute the query and fetch all results
        logger.info("\tgot db connection")
        recent_votes = conn.execute(
            sqlalchemy.text(
                "SELECT candidate, time_cast FROM votes ORDER BY time_cast DESC LIMIT 5"
            )
        ).fetchall()
        logger.info("\tgot votes")
        # Convert the results into a list of dicts representing votes
        for row in recent_votes:
            votes.append({"candidate": row[0], "time_cast": row[1]})

        stmt = sqlalchemy.text(
            "SELECT COUNT(vote_id) FROM votes WHERE candidate=:candidate"
        )
        logger.info("\t built sql text")
        # Count number of votes for tabs
        tab_count = conn.execute(stmt, parameters={"candidate": "TABS"}).scalar()
        logger.info("\tgot tab count")
        # Count number of votes for spaces
        space_count = conn.execute(stmt, parameters={"candidate": "SPACES"}).scalar()
        logger.info("\tgot space count")

    return {
        "space_count": space_count,
        "recent_votes": votes,
        "tab_count": tab_count,
    }


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
