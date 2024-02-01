import logging
from http.client import (
    BAD_REQUEST,
    CREATED,
    UNAUTHORIZED,
    UNPROCESSABLE_ENTITY,
    CONFLICT,
    NOT_FOUND,
    OK,
)
from api.utils import class_route, commit_entity_or_abort
from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request, require_admin_user
from flask import Blueprint, abort, request
from flask.views import MethodView
from marshmallow import ValidationError
from models.database import db
from schemas.community_thread import (
    CommunityThreadSchema,
    CommunityThreadCreateSchema,
    group_message_schema_from_community_thread,
)
from models.community_thread import CommunityThread, ThreadParticipants
from models.thread_post import ThreadPost
from schemas.thread_post import ThreadPostSchema, ThreadPostCreateSchema
from api.constants import V1_API_PREFIX
from api.utils import generate_paginated_dict


community_thread_endpoints = Blueprint(
    # "Community Threads", __name__, url_prefix=f"{V1_API_PREFIX}/community-threads"
    "Community Threads",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/chats/group-conversations",
)


@class_route(community_thread_endpoints, "/", "community_thread_list")
class CommunityThreadListView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        # TODO: optimize to pull the set of joined/unjoined from the db instead of filtering in python
        user_threads = (
            db.session.query(ThreadParticipants.thread_id)
            .where(ThreadParticipants.user_profile_id == user.id)
            .all()
        )
        user_thread_ids = [thread[0] for thread in user_threads]
        joined_community_threads = (
            db.session.query(CommunityThread)
            .where(CommunityThread.id.in_(user_thread_ids))
            .where(CommunityThread.active.is_(True))
            .all()
        )

        unjoined_community_threads = (
            db.session.query(CommunityThread)
            .where(CommunityThread.id.notin_(user_thread_ids))
            .all()
        )

        joined_group_messages = [
            group_message_schema_from_community_thread(thread, True)
            for thread in joined_community_threads
        ]
        not_joined_group_messagees = [
            group_message_schema_from_community_thread(thread, False)
            for thread in unjoined_community_threads
        ]
        results = joined_group_messages + not_joined_group_messagees
        return generate_paginated_dict(results)

    @jwt_authenticated
    def put(self):
        user = get_user_from_request(request)
        require_admin_user(user)

        json_data = request.get_json()
        if not json_data:
            abort(BAD_REQUEST, "No input data provided.")

        schema = CommunityThreadCreateSchema()

        try:
            data = schema.load(json_data)
        except ValidationError as err:
            abort(UNPROCESSABLE_ENTITY, err.messages)

        thread = CommunityThread(
            display_name=data["display_name"],
            description=data["description"],
            owner_id=user.admin_profiles.id,
            participants=[user],
        )
        commit_entity_or_abort(thread)
        result = CommunityThreadSchema().dump(thread)
        return result, CREATED


@community_thread_endpoints.route("/<int:thread_id>/", methods=["GET"])
@jwt_authenticated
def get_community_thread(thread_id: int):
    user = get_user_from_request(request)
    community_thread = (
        db.session.query(CommunityThread)
        .where(CommunityThread.id == thread_id)
        .join(CommunityThread.participants)
        .one_or_none()
    )

    belong_to = any(
        participant
        for participant in community_thread.participants
        if participant.id == user.id
    )

    return group_message_schema_from_community_thread(community_thread, belong_to)


@class_route(
    community_thread_endpoints, "/<int:thread_id>/posts/", "community_thread_posts"
)
class ThreadPostListView(MethodView):
    @jwt_authenticated
    def get(thread_id: int):
        posts = (
            db.session.query(ThreadPost).where(CommunityThread.id == thread_id).all()
        )
        schema = ThreadPostSchema()

        return generate_paginated_dict(schema.dump(posts, many=True))

    # @jwt_authenticated
    # def post(thread_id: int):
    #     user = get_user_from_request(request)
    #     thread = (
    #         db.session.query(CommunityThread)
    #         .where(CommunityThread == thread_id)
    #         .one_or_none()
    #     )
    #     if thread is None:
    #         abort(NOT_FOUND, f"Thread {thread_id} not found")

    #     user_belongs_to_thread = any(
    #         participant
    #         for participant in thread.participants
    #         if participant.id == user.id
    #     )

    #     if user_belongs_to_thread:
    #         abort(
    #             UNAUTHORIZED, "Cannot post to a group messagee that you haven't joined"
    #         )
    #     try:
    #         post_data = ThreadPostCreateSchema().load(request.get_json())
    #     except ValidationError as err:
    #         abort(UNPROCESSABLE_ENTITY, err.messages)

    #     post = ThreadPost(author_id=user, thread_id=, content=)

    #     return generate_paginated_dict(schema.dump(posts, many=True))


@community_thread_endpoints.route("/<int:thread_id>/", methods=["POST"])
@jwt_authenticated
def update_community_thread(thread_id: int):
    user = get_user_from_request(request)
    require_admin_user(user)
    json_data = request.get_json()
    if not json_data:
        abort(BAD_REQUEST, "No input data provided.")

    schema = CommunityThreadCreateSchema(partial=True)

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        abort(UNPROCESSABLE_ENTITY, err.messages)

    thread = db.session.get(CommunityThread, thread_id)
    if thread is None:
        abort(NOT_FOUND, f"Thread {thread_id} not found")

    # TODO: flesh out as more edit capability is needed
    if data.get("display_name"):
        thread.display_name = data["display_name"]
    if data.get("active"):
        thread.active = data["active"]

    commit_entity_or_abort(thread)

    result = CommunityThreadSchema().dump(thread)
    return result, OK


@community_thread_endpoints.route("/<int:thread_id>/join/", methods=["GET"])
@jwt_authenticated
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
    commit_entity_or_abort(community_thread)


@community_thread_endpoints.route("/<int:thread_id>/leave/", methods=["GET"])
@jwt_authenticated
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
    commit_entity_or_abort(community_thread)
