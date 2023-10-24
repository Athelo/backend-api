from flask import Blueprint, request
from auth.middleware import jwt_authenticated

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


@main_endpoints.route("/protected", methods=["GET"])
@jwt_authenticated
def protected():
    return f"{request.uid} is authenticated"
