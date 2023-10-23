from athelo import app
from flask import Blueprint

main_endpoints = Blueprint("Main", __name__)


@app.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"
