from http.client import CREATED, NOT_FOUND, OK, UNAUTHORIZED

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, abort, request
from flask.views import MethodView
from models.community_thread import CommunityThread
from models.database import db
from models.thread_post import ThreadPost
from repositories.utils import commit_entity
from schemas.thread_post import ThreadPostCreateSchema, ThreadPostSchema

from api.constants import V1_API_PREFIX
from api.utils import class_route, generate_paginated_dict, validate_json_body

thread_post_endpoints = Blueprint(
    "Thread Posts",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/community-threads/<int:thread_id>/posts",
)


@class_route(thread_post_endpoints, "/", "community_thread_posts")
class ThreadPostListView(MethodView):
    @jwt_authenticated
    def get(self, thread_id: int):
        posts = (
            db.session.query(ThreadPost)
            .where(ThreadPost.thread_id == thread_id)
            .order_by(ThreadPost.created_at)
            .all()
        )
        schema = ThreadPostSchema()

        return generate_paginated_dict(schema.dump(posts, many=True)), OK

    @jwt_authenticated
    def put(self, thread_id: int):
        user = get_user_from_request(request)
        thread = (
            db.session.query(CommunityThread)
            .filter(CommunityThread.id == thread_id)
            .one_or_none()
        )
        if thread is None:
            abort(NOT_FOUND, f"Thread {thread_id} not found")

        user_belongs_to_thread = any(
            participant
            for participant in thread.participants
            if participant.id == user.id
        )

        if not user_belongs_to_thread:
            abort(
                UNAUTHORIZED, "Cannot post to a group messagee that you haven't joined"
            )

        schema = ThreadPostCreateSchema()
        data = validate_json_body(schema)

        post = ThreadPost(
            author_id=user.id, thread_id=thread_id, content=data["content"]
        )

        commit_entity(post)

        return ThreadPostSchema().dump(post), CREATED
