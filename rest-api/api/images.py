from http.client import (
    CREATED,
)

from auth.middleware import jwt_authenticated
from flask import Blueprint
from schemas.image_upload import ImageUploadSchema
from services.cloud_storage import CloudStorageService

from api.constants import V1_API_PREFIX
from api.utils import validate_json_body

image_endpoints = Blueprint(
    "Images",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/common/image",
)


@jwt_authenticated
@image_endpoints.route("/", methods=["POST"])
def upload_image():
    cloudStorageService = CloudStorageService.instance()
    schema = ImageUploadSchema()
    data = validate_json_body(schema)

    name = data["name"]
    img_data = str.split(data["data"], ",")[-1]
    file_type = data["file_type"]

    return {"url": cloudStorageService.upload_image(name, img_data, file_type)}, CREATED
