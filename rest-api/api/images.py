from http.client import (
    BAD_REQUEST,
    CREATED,
    UNPROCESSABLE_ENTITY,
)

from marshmallow import ValidationError
from api.constants import ABOUT_US, PRIVACY, TERMS_OF_USE
from api.utils import class_route, commit_entity_or_abort
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
from services.cloud_storage import CloudStorageService
from schemas.image_upload import ImageUploadSchema
from flask import current_app as app


image_endpoints = Blueprint(
    "Images",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/images",
)


@jwt_authenticated
@image_endpoints.route("/", methods=["POST"])
def upload_image():
    cloudStorageService = CloudStorageService.instance()
    json_data = request.get_json()
    schema = ImageUploadSchema()
    try:
        request_data = schema.load(json_data)
    except ValidationError as err:
        abort(UNPROCESSABLE_ENTITY, err.messages)

    name = request_data["name"]
    data = str.split(request_data["data"], ",")[-1]
    file_type = request_data["file_type"]

    return {"url": cloudStorageService.upload_image(name, data, file_type)}, CREATED
