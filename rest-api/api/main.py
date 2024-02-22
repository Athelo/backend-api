from datetime import datetime
from http.client import ACCEPTED

from auth.middleware import jwt_authenticated
from flask import Blueprint, request
from flask import current_app as app

from api.constants import V1_API_PREFIX

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/public/", methods=["GET"])
def public():
    return f"This is Athelo Health's API, and it is {datetime.utcnow()}"


@main_endpoints.route("/protected/", methods=["GET"])
@jwt_authenticated
def protected():
    return f"{request.uid} ({request.email}) is authenticated at {datetime.utcnow()}"


@main_endpoints.route(f"{V1_API_PREFIX}/test-logging/")
def test_logging():
    app.logger.critical("This is a critical log")
    app.logger.fatal("This is a fatal log")
    app.logger.error("This is an error log")
    app.logger.warn("This is a warn log")
    app.logger.warning("This is a warning log")
    app.logger.info("This is an info log")
    app.logger.debug("This is a debug log")
    return "", ACCEPTED
