import imghdr
import io
from base64 import b64encode
from http.client import (
    CREATED,
)
from os import path

from auth.middleware import jwt_authenticated
from flask import Blueprint, abort, request
from flask import current_app as app
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
def upload_image():
    cloudStorageService = CloudStorageService.instance()
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

    file_data = uploaded_file.read()

    value_as_a_stream = io.BytesIO(file_data)  # io.BytesIO
    uploaded_file_url = cloudStorageService.upload_file(
        filename,
        value_as_a_stream,
        len(file_data),
        file_type=uploaded_file.mimetype,
    )

    return {"url": uploaded_file_url}, CREATED


@jwt_authenticated
@image_endpoints.route("/json/", methods=["POST"])
def upload_image_json():
    cloudStorageService = CloudStorageService.instance()
    schema = ImageUploadSchema()
    data = validate_json_body(schema)

    name = data["name"]
    img_data = str.split(data["data"], ",")[-1]
    file_type = data["file_type"]

    return {"url": cloudStorageService.upload_image(name, img_data, file_type)}, CREATED
