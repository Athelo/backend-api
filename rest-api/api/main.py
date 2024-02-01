from datetime import datetime
import logging

from auth.middleware import jwt_authenticated
from threading import Lock
from flask import (
    Blueprint,
    render_template,
    request,
)
from flask import current_app as app
from services.zoom import make_zoom_authorization_url
from api.constants import V1_API_PREFIX
from http.client import ACCEPTED

logger = logging.getLogger()

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
    # token = OpenTokClient.instance().create_host_token(session_id, user)
    return render_template("opentok.html", api_key=key)


@main_endpoints.route(f"{V1_API_PREFIX}/test-logging")
def test_logging():
    logger.critical("This is a critical log")
    logger.fatal("This is a fatal log")
    logger.error("This is an error log")
    logger.warn("This is a warn log")
    logger.warning("This is a warning log")
    logger.info("This is an info log")
    logger.debug("This is a debug log")
    return "", ACCEPTED
