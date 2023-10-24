from flask import Blueprint

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"
