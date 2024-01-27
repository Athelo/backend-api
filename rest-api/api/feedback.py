import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNPROCESSABLE_ENTITY,
)
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.database import db
from models.feedback_topic import FeedbackTopic
from models.feedback import Feedback
from api.constants import V1_API_PREFIX
from api.utils import generate_paginated_dict
from auth.utils import require_admin_user
from sqlalchemy.exc import IntegrityError, DatabaseError


logger = logging.getLogger()

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
            print(exc)
            abort(UNPROCESSABLE_ENTITY)

        try:
            db.session.add(topic)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create feedback topic because {e.orig.args[0]['M']}",
            )
        except DatabaseError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create feedback topic because {e.orig.args[0]['M']}",
            )
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
        except Exception as exc:
            print(exc)
            abort(UNPROCESSABLE_ENTITY)

        try:
            db.session.add(feedback)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create chat because {e.orig.args[0]['M']}",
            )
        except DatabaseError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create chat because {e.orig.args[0]['M']}",
            )
        result = feedback.to_json()
        return result, CREATED
