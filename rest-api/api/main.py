from datetime import datetime
from http.client import ACCEPTED

from auth.middleware import jwt_authenticated
from flask import Blueprint, render_template, request
from flask import current_app as app
from services.zoom import make_zoom_authorization_url

from api.constants import V1_API_PREFIX

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


@main_endpoints.route("/public/", methods=["GET"])
def public():
    return f"This is Athelo Health's API, and it is {datetime.utcnow()}"


@main_endpoints.route("/protected/", methods=["GET"])
@jwt_authenticated
def protected():
    return f"{request.uid} ({request.email}) is authenticated at {datetime.utcnow()}"


@main_endpoints.route("/dev/", methods=["GET"])
def render_index() -> str:
    """Serves the dev tools page of the app."""
    return render_template("dev.html")


@main_endpoints.route(
    "/zoom/",
)
def zoom_homepage():
    text = '<a href="%s">Authenticate with Zoom</a>'
    return text % make_zoom_authorization_url()


@main_endpoints.route("/opentok/")
def opentok():
    key = app.config.get("VONAGE_API_KEY")
    return render_template("opentok.html", api_key=key)


@main_endpoints.route("/images/")
def images():
    return render_template("image_upload.html")


@main_endpoints.route(f"{V1_API_PREFIX}/test-logging")
def test_logging():
    app.logger.critical("This is a critical log")
    app.logger.fatal("This is a fatal log")
    app.logger.error("This is an error log")
    app.logger.warn("This is a warn log")
    app.logger.warning("This is a warning log")
    app.logger.info("This is an info log")
    app.logger.debug("This is a debug log")
    return "", ACCEPTED
