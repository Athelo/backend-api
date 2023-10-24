import logging
from flask import Blueprint, render_template, request, Response
from sqlalchemy import func
from models import db
from models.vote import Vote

logger = logging.getLogger()
# Create a user blueprint
vote_endpoints = Blueprint("Vote", __name__, url_prefix="/votes")


@vote_endpoints.route("/", methods=["GET"])
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


@vote_endpoints.route("/", methods=["POST"])
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
