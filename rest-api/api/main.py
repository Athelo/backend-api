from datetime import datetime

from auth.middleware import jwt_authenticated
from flask import Blueprint, render_template, request

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


@main_endpoints.route("/public", methods=["GET"])
def public():
    return f"This is Athelo Health's API, and it is {datetime.utcnow()}"


@main_endpoints.route("/protected", methods=["GET"])
@jwt_authenticated
def protected():
    return f"{request.uid} ({request.email}) is authenticated at {datetime.utcnow()}"


@main_endpoints.route("/dev", methods=["GET"])
def render_index() -> str:
    """Serves the dev tools page of the app."""
    return render_template("dev.html")