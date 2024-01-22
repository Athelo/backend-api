from flask import session, redirect, url_for, render_template, request, Blueprint

from auth.utils import get_user_from_request
from models.users import Users

real_time_chat_endpoints = Blueprint(
    "real_time_chat", __name__, url_prefix="/real-time-chat"
)


@real_time_chat_endpoints.route("/", methods=["GET", "POST"])
def index():
    """Login form to enter a room."""
    # if form.validate_on_submit():
    #     session["name"] = form.name.data
    #     session["room"] = form.room.data
    #     return redirect(url_for(".chat"))
    # elif request.method == "GET":
    #     form.name.data = session.get("name", "")
    #     form.room.data = session.get("room", "")

    if request.method == "GET":
        return render_template("chat_index.html")
    else:
        print(request.form)
        session["room"] = request.form["roomname"]
        session["name"] = request.form["displayName"]
        return redirect(url_for(".chat"))


@real_time_chat_endpoints.route("/chatroom")
def chat():
    """Chat room. The user's name and room must be stored in
    the session."""
    print(session)
    name = session.get("name", "")
    room = session.get("room", "")
    print(name)
    print(room)
    if name == "" or room == "":
        return redirect(url_for(".index"))
    return render_template("chat.html", name=name, room=room)
