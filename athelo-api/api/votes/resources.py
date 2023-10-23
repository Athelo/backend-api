from flask_smorest import Blueprint
from flask import MethodView

votes_endpoints = Blueprint(
    "Votes",
    __name__,
    url_prefix="/votes/",
    description="Operations on votes from the starter app",
)


@votes_endpoints.route("/")
class VotesList(MethodView):
    @votes_endpoints.response(200, VoteSummarySchema)
    def get(self):
        return Symptoms.query.all()
