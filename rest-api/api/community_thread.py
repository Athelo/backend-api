import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
    CONFLICT,
    NOT_FOUND,
)
from api.utils import class_route
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.community_thread import (
    CommunityThreadSchema,
    CommunityThreadCreateSchema,
    group_message_schema_from_community_thread,
)
from models.community_thread import CommunityThread
from sqlalchemy.exc import IntegrityError
from api.constants import V1_API_PREFIX
from api.utils import generate_paginated_dict


logger = logging.getLogger()

community_thread_endpoints = Blueprint(
    # "Community Threads", __name__, url_prefix=f"{V1_API_PREFIX}/community-threads"
    "Community Threads",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/chats/group-conversations",
)


@class_route(community_thread_endpoints, "/", "")
class CommunityThreadListView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        # TODO: optimize to pull the set of joined/unjoined from the db instead of filtering in python
        community_threads = (
            db.session.query(CommunityThread).join(CommunityThread.users).all()
        )

        joined = [
            group_message_schema_from_community_thread(thread, True)
            for thread in community_threads
            if user in thread.participants
        ]
        not_joined = [
            group_message_schema_from_community_thread(thread, False)
            for thread in set(community_threads) - set(joined)
        ]
        results = joined + not_joined
        generate_paginated_dict(results)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        if user.admin_profiles is None:
            abort(UNAUTHORIZED, "Only admins can create new community threads")

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")

        schema = CommunityThreadCreateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        thread = CommunityThread(
            display_name=data["display_name"], owner=user, participants=[user]
        )
        try:
            db.session.add(thread)
            db.session.commit()
        except IntegrityError as e:
            abort(
                UNPROCESSABLE_ENTITY,
                f"Cannot create chat because {e.orig.args[0]['M']}",
            )
        result = CommunityThreadSchema().dump(thread)
        return result, CREATED


@community_thread_endpoints.route("/<int:thread_id>", methods=["GET"])
def get_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.users)
        .one_or_none()
    )

    belong_to = any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    )

    return group_message_schema_from_community_thread(community_thread, belong_to)


@jwt_authenticated
@community_thread_endpoints.route("/<int:thread_id>/join", methods=["GET"])
def join_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.users)
        .one_or_none()
    )

    if community_thread is None:
        abort(NOT_FOUND, f"thread {thread_id} does not exist")

    if any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    ):
        abort(CONFLICT, "user is already in the thread")

    community_thread.participants.append(user)

    try:
        db.session.add(community_thread)
        db.session.commit()
    except IntegrityError as e:
        abort(
            UNPROCESSABLE_ENTITY,
            f"Cannot join community thread because {e.orig.args[0]['M']}",
        )


@jwt_authenticated
@community_thread_endpoints.route("/<int:thread_id>/leave", methods=["GET"])
def leave_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.users)
        .one_or_none()
    )

    if community_thread is None:
        abort(NOT_FOUND, f"thread {thread_id} does not exist")

    if not any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    ):
        abort(CONFLICT, "user is not in thread")

    community_thread.participants.remove(user)

    try:
        db.session.add(community_thread)
        db.session.commit()
    except IntegrityError as e:
        abort(
            UNPROCESSABLE_ENTITY,
            f"Cannot join community thread because {e.orig.args[0]['M']}",
        )
