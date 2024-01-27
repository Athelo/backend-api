from datetime import datetime
from http.client import NOT_FOUND, FORBIDDEN, BAD_REQUEST, UNAUTHORIZED

from flask import Blueprint, request, jsonify, abort
from flask_socketio import leave_room, join_room, send

from utils.flask_request_utils import get_request_json_dict_or_raise_exception
from utils.socketio_utils import generate_room_code, generate_token, decode_token
from websocket.socketio import rooms, users_dump

socket_endpoints = Blueprint("Socket Connection", __name__, url_prefix="/api/v1/chats/")


@socket_endpoints.post("/sign-in")
def sign_in():
    """
    User sign in
    """
    request_body = get_request_json_dict_or_raise_exception(request)
    user_name = request_body.get("userName")

    if user_name in users_dump:
        return jsonify(users_dump.get(user_name))

    user_id = len(users_dump.keys()) + 1
    user = {
        "id": user_id,
        "name": user_name,
        "rooms": [],
        "newUser": True,
    }
    users_dump[user_name] = user

    return jsonify(user)


@socket_endpoints.get("/rooms/")
def get_rooms_for_user():
    """
    Get all rooms for a user
    """
    user_name = request.headers.get("userName")
    if user_name not in users_dump:
        abort(UNAUTHORIZED, "User does not exist")

    return jsonify(users_dump[user_name]["rooms"])


@socket_endpoints.post("/room/")
def create_room():
    """
    Create a room
    """
    body = get_request_json_dict_or_raise_exception(request)
    user_name = body.get("userName")
    room_name = body.get("roomName")
    room_code = generate_room_code(6, list(rooms.keys()))

    new_room = {
        "id": len(rooms.keys()) + 1,
        "name": room_name,
        "code": room_code,
        "onlineUsers": [],
        "messages": [
            {
                "id": 1,
                "sender": "",
                "text": f"{user_name} has created the chat",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ],
        'members_count': 1,
        'members': [user_name],
        'creator': user_name,
        'device_identifiers': ["device_identifier"]
    }
    rooms[room_code] = new_room

    return jsonify(new_room)


@socket_endpoints.get("/room/<room_code>/")
def get_room_info(room_code: str):
    """
    Get room info
    """

    if room_code not in rooms:
        abort(NOT_FOUND, "Room does not exist")

    user_name = request.headers.get("userName")
    if user_name not in rooms[room_code]["members"]:
        abort(FORBIDDEN, "User is not a member of the room")

    online_users = rooms[room_code].get("onlineUsers", [])
    online_users.append(user_name)
    rooms[room_code]["onlineUsers"] = list(set(online_users))
    token = generate_token(user_name, room_code, "device_identifier")
    return jsonify({
        "room_info": rooms[room_code],
        "websocket_token": token
    })


@socket_endpoints.post("/sessions/create-session")
def create_session():
    """
    Create a new session
    """
    request_body = get_request_json_dict_or_raise_exception(request)
    user_name = request_body.get("userName")
    room_name = request_body.get("roomName")
    device_identifier = request_body.get("device_identifier")

    room_code = generate_room_code(6, list(rooms.keys()))
    new_room = {
        'members_count': 1,
        'members': [user_name],
        'messages': [
            {
                "sender": "",
                "message": f"{user_name} has created the chat",
                "time": datetime.now().strftime("%H:%M:%S")
            }
        ],
        'name': room_name,
        'creator': user_name,
        'code': room_code,
        'device_identifiers': [device_identifier]
    }
    rooms[room_code] = new_room
    token = generate_token(user_name, room_code, device_identifier)

    return jsonify({
        "token": token,
        "room_info": new_room
    })


@socket_endpoints.post("/sessions/open-session")
def open_session():
    """
    Open(Join) a session
    """
    request_body = get_request_json_dict_or_raise_exception(request)
    user_name = request_body.get("userName")
    room_code = request_body.get("roomCode")
    device_identifier = request_body.get("device_identifier")

    if room_code not in rooms:
        leave_room(room_code)

    join_room(room_code)
    send({
        "sender": "",
        "message": f"{user_name} has entered the chat"
    }, to=room_code)
    rooms[room_code]["members_count"] += 1
    rooms[room_code]["members"].append(user_name)
    rooms[room_code]["device_identifiers"].append(device_identifier)

    token = generate_token(user_name, room_code, device_identifier)

    return jsonify({
        "token": token,
        "room_info": rooms[room_code]
    })


@socket_endpoints.post("/sessions/close-session")
def close_session():
    """
    Close a session
    """
    request_body = get_request_json_dict_or_raise_exception(request)
    token = request_body.get("token")
    user_name, room_code, device_identifier = decode_token(token)

    if room_code not in rooms:
        abort(NOT_FOUND, "Room does not exist")

    if device_identifier not in rooms[room_code]["device_identifiers"]:
        abort(BAD_REQUEST, "Device identifier does not exist")

    rooms[room_code]["members_count"] -= 1
    rooms[room_code]["members"].remove(user_name)
    rooms[room_code]["device_identifiers"].remove(device_identifier)

    if rooms[room_code]["members_count"] <= 0:
        del rooms[room_code]

    send({
        "sender": "",
        "message": f"{user_name} has left the chat"
    }, to=room_code)

    return jsonify({
        "message": "Session closed successfully"
    })
