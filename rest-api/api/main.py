from datetime import datetime

from auth.middleware import jwt_authenticated
from flask import Blueprint, render_template, request

main_endpoints = Blueprint("Main", __name__)


@main_endpoints.route("/", methods=["GET"])
def hello_world():
    return "Hello World! This is Athelo Health's API"


@main_endpoints.route("/api/v1/public", methods=["GET"])
def public():
    return f"This is Athelo Health's API, and it is {datetime.utcnow()}"


@main_endpoints.route("/api/v1/protected", methods=["GET"])
@jwt_authenticated
def protected():
    return f"{request.uid} ({request.email}) is authenticated at {datetime.utcnow()}"


@main_endpoints.route("/dev", methods=["GET"])
def render_index() -> str:
    """Serves the dev tools page of the app."""
    return render_template("dev.html")


def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    while True:
        socketio.sleep(10)
        count += 1
        socketio.emit("my_response", {"data": "Server generated event", "count": count})


@main_endpoints.route("/chat_index")
def index():
    return render_template("chat_index.html", async_mode=socketio.async_mode)


@socketio.event
def my_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit("my_response", {"data": message["data"], "count": session["receive_count"]})


@socketio.event
def my_broadcast_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": message["data"], "count": session["receive_count"]},
        broadcast=True,
    )


@socketio.event
def join(message):
    join_room(message["room"])
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": "In rooms: " + ", ".join(rooms()), "count": session["receive_count"]},
    )


@socketio.event
def leave(message):
    leave_room(message["room"])
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": "In rooms: " + ", ".join(rooms()), "count": session["receive_count"]},
    )


@socketio.on("close_room")
def on_close_room(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {
            "data": "Room " + message["room"] + " is closing.",
            "count": session["receive_count"],
        },
        to=message["room"],
    )
    close_room(message["room"])


@socketio.event
def my_room_event(message):
    session["receive_count"] = session.get("receive_count", 0) + 1
    emit(
        "my_response",
        {"data": message["data"], "count": session["receive_count"]},
        to=message["room"],
    )


@socketio.event
def disconnect_request():
    @copy_current_request_context
    def can_disconnect():
        disconnect()

    session["receive_count"] = session.get("receive_count", 0) + 1
    # for this emit we use a callback function
    # when the callback function is invoked we know that the message has been
    # received and it is safe to disconnect
    emit(
        "my_response",
        {"data": "Disconnected!", "count": session["receive_count"]},
        callback=can_disconnect,
    )


@socketio.event
def my_ping():
    emit("my_pong")


@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit("my_response", {"data": "Connected", "count": 0})


@socketio.on("disconnect")
def test_disconnect():
    print("Client disconnected", request.sid)
