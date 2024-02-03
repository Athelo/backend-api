from http.client import (
    BAD_REQUEST,
    CREATED,
    UNPROCESSABLE_ENTITY,
)

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.database import db
from models.feedback import Feedback
from models.feedback_topic import FeedbackTopic
from repositories.utils import commit_entity

from api.constants import ABOUT_US, PRIVACY, TERMS_OF_USE, V1_API_PREFIX
from api.utils import class_route, generate_paginated_dict

feedback_endpoints = Blueprint(
    "Feedback", __name__, url_prefix=f"{V1_API_PREFIX}/applications/"
)


@class_route(feedback_endpoints, "/feedback-topic/", "feedback_topics")
class FeedbackTopicsView(MethodView):
    @jwt_authenticated
    def get(self):
        topics = db.session.query(FeedbackTopic).all()
        results = [topic.to_json() for topic in topics]
        return generate_paginated_dict(results)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        require_admin_user(user)

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")

        topic = None
        try:
            topic = FeedbackTopic(name=json_data["name"])
        except Exception as exc:
            abort(UNPROCESSABLE_ENTITY, exc)

        commit_entity(topic)
        result = topic.to_json()
        return result, CREATED


@class_route(feedback_endpoints, "/feedback/", "feedback")
class FeedbackListView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        require_admin_user(user)

        feedbacks = db.session.query(Feedback).all()
        return generate_paginated_dict([feedback.to_json() for feedback in feedbacks])

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")

        feedback = None
        try:
            feedback = Feedback(
                author_id=user.id,
                content=json_data["content"],
                topic_id=json_data["topic_id"],
            )
        except Exception:
            abort(UNPROCESSABLE_ENTITY)

        commit_entity(feedback)
        result = feedback.to_json()
        return result, CREATED


@class_route(feedback_endpoints, "/applications/", "about_us")
class ApplicationData(MethodView):
    def get(self):
        # Return app auxillary data (e.g. about us, privacy policy and terms of use)
        res = [{"about_us": ABOUT_US, "privacy": PRIVACY, "terms_of_use": TERMS_OF_USE}]

        return generate_paginated_dict(res)
