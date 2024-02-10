import imghdr
from base64 import b64encode
from http.client import (
    CREATED,
)
from os import path

from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from flask import current_app as app
from inject import autoparams
from schemas.image_upload import ImageUploadSchema
from services.cloud_storage import CloudStorageService
from werkzeug.utils import secure_filename

from api.constants import V1_API_PREFIX
from api.utils import validate_json_body

image_endpoints = Blueprint(
    "Images",
    __name__,
    url_prefix=f"{V1_API_PREFIX}/common/image",
)


def validate_image(stream):
    header = stream.read(512)  # 512 bytes should be enough for a header check
    stream.seek(0)  # reset stream pointer
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


@jwt_authenticated
@image_endpoints.route("/", methods=["POST"])
@autoparams()
def upload_image(cloud_storage_service: CloudStorageService):
    try:
        uploaded_file = request.files["file"]
    except Exception as e:
        app.logger.error(e)
        raise e

    filename = secure_filename(uploaded_file.filename)
    if filename != "":
        file_ext = path.splitext(filename)[1]
        if file_ext not in app.config["UPLOAD_EXTENSIONS"]:
            message = f"{file_ext} is not in allowed file extensions: {app.config['UPLOAD_EXTENSIONS']}"
            app.logger.error(message)
            abort(400, message)

        validated_ext = validate_image(uploaded_file.stream)
        if file_ext != validated_ext:
            message = f"File extension {file_ext} doesn't match extension in image data {validated_ext}"
            app.logger.error(message)
            abort(400, message)

    image_bytes = uploaded_file.read()
    image_data = b64encode(image_bytes)

    return {
        "url": cloud_storage_service.upload_image(
            filename, image_data, uploaded_file.content_type
        )
    }, CREATED


@jwt_authenticated
@image_endpoints.route("/json/", methods=["POST"])
@autoparams()
def upload_image_json(cloud_storage_service: CloudStorageService):
    schema = ImageUploadSchema()
    data = validate_json_body(schema)

    name = data["name"]
    img_data = str.split(data["data"], ",")[-1]
    file_type = data["file_type"]

    return {
        "url": cloud_storage_service.upload_image(name, img_data, file_type)
    }, CREATED
