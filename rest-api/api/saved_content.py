from http.client import CREATED, OK

from auth.middleware import jwt_authenticated
from auth.utils import get_user_from_request
from flask import Blueprint, request
from flask.views import MethodView
from models.database import db
from models.saved_content import SavedContent
from repositories.utils import commit_entity
from schemas.saved_content import SavedContentCreateUpdateSchema, SavedContentSchema

from api.utils import class_route, validate_json_body

saved_content_endpoints = Blueprint(
    "My Saved Content", __name__, url_prefix="/api/v1/saved-content"
)


@class_route(saved_content_endpoints, "/", "saved_content")
class SavedContentView(MethodView):
    @jwt_authenticated
    def get(self):
        user = get_user_from_request(request)
        content = (
            db.session.query(SavedContent).filter_by(user_profile_id=user.id).all()
        )
        schema = SavedContentSchema(many=True)
        return schema.dump(content)

    @jwt_authenticated
    def post(self):
        user = get_user_from_request(request)
        schema = SavedContentCreateUpdateSchema()
        data = validate_json_body(schema)

        saved_content = SavedContent(
            external_content_id=data["external_content_id"], user_profile_id=user.id
        )
        commit_entity(saved_content)
        result = schema.dump(saved_content)
        return result, CREATED

    @jwt_authenticated
    def delete(self):
        user = get_user_from_request(request)
        schema = SavedContentSchema(partial=True)
        data = validate_json_body(schema)

        saved_content = (
            db.session.query(SavedContent)
            .filter_by(
                user_profile_id=user.id, external_content_id=data["external_content_id"]
            )
            .one()
        )

        db.session.delete(saved_content)
        db.session.commit()
        result = schema.dump(saved_content)
        return result, OK
