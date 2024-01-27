from datetime import datetime

from flask import request
from flask_socketio import SocketIO, emit

from auth.middleware import websocket_jwt_authenticated
from websocket.dump import TEST_ROOMS, TEST_USERS_DUMP

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "eventlet"
rooms = TEST_ROOMS
users = []
users_dump = TEST_USERS_DUMP
session_ids_to_user = {}


def setup_socketio(app):
    socketio = SocketIO(async_mode=async_mode, logger=True, engineio_logger=True, cors_allowed_origins=app.config.get("CORS_ALLOWED_ORIGINS", "*"))
    socketio.init_app(app)

    @socketio.on("connect")
    def connect(data):
        print("Client connected")
        emit("connectResponse", data)

    @socketio.on("sign_in")
    def join(data):
        print("Client signed in")
        print(request.sid)
        user_name = data.get("userName")
        emit("signInResponse", data)

    @socketio.on("join_room")
    def join(data):
        print("Client joined a room")
        user_name = data.get("userName")
        room_code = data.get("roomCode")

        session_ids_to_user[request.sid] = f"{user_name}:{room_code}"

        online_users = rooms[room_code].get("onlineUsers", [])
        online_users.append(user_name)
        rooms[room_code]["onlineUsers"] = list(set(online_users))
        emit("joinRoomResponse", rooms[room_code]["onlineUsers"], broadcast=True)

    @socketio.on("message")
    @websocket_jwt_authenticated
    def message(data):
        print("Client message")
        room_code = data.get("roomCode")
        message_id = len(rooms[room_code]['messages']) + 1
        new_msg = {
            "id": message_id,
            "sender": data.get("sender"),
            "text": data.get("text"),
            "time": datetime.now().strftime("%H:%M:%S")
        }
        rooms[room_code]['messages'].append(new_msg)
        emit("messageResponse", new_msg, broadcast=True)

    @socketio.on("typing")
    @websocket_jwt_authenticated
    def typing(data):
        print("Client typing")
        emit("typingResponse", data, broadcast=True)

    @socketio.on("newUser")
    def new_user(data):
        print("New user")
        users.append(data)
        emit("newUserResponse", users, broadcast=True)

    @socketio.on("disconnect")
    def disconnect():
        print("Client disconnected")
        data = session_ids_to_user[request.sid]
        user_name, room_code = tuple(data.split(":"))
        rooms[room_code]["onlineUsers"].remove(user_name)
        emit("userDisconnectedResponse", rooms[room_code]["onlineUsers"], broadcast=True)

    return socketio
