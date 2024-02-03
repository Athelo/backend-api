from http.client import (
    CREATED,
    UNPROCESSABLE_ENTITY,
)

from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from marshmallow import ValidationError
from schemas.image_upload import ImageUploadSchema
from services.cloud_storage import CloudStorageService

from api.constants import V1_API_PREFIX

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
