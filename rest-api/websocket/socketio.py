from flask import request
from flask_socketio import SocketIO, emit

from auth.middleware import websocket_jwt_authenticated
from cache import cache
from models import MessageChannel, Message
from models.database import db

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "eventlet"
users = []
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
        emit("signInResponse", data)

    @socketio.on("join_message_channel")
    def join(data):
        print("Client joined a message channel")
        user_id = data.get("userId")
        message_channel_id = data.get("messageChannelId")
        cache_channel_key = f"message_channel_{message_channel_id}"

        cache.set(f"user_session_{request.sid}", f"{user_id}:{message_channel_id}")
        channel_online_users = cache.get(cache_channel_key)
        if not channel_online_users:
            channel_online_users = []

        channel_online_users.add(user_id)
        cache.set(cache_channel_key, channel_online_users)
        emit("joinMessageChannelResponse", list(channel_online_users), broadcast=True)

    @socketio.on("message")
    @websocket_jwt_authenticated
    def message(data):
        print("Client message")
        message_channel_id = data.get("messageChannelId")
        sender_name = data.get("senderName")
        content = data.get("text")

        message_channel = db.session.get(MessageChannel, message_channel_id)
        msg = Message(
            author_id=request.uid,
            content=content,
            channel_id=message_channel_id,
            channel=message_channel,
        )
        db.session.add(msg)
        db.session.commit()

        new_msg = {
            "id": msg.id,
            "sender": sender_name,
            "text": content,
            "time": msg.created_at.strftime("%H:%M:%S")
        }
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
        user_session = cache.get(f"user_session_{request.sid}")
        if not user_session:
            return

        user_id, message_channel_id = tuple(user_session.split(":"))
        cache_channel_key = f"message_channel_{message_channel_id}"

        channel_online_users = cache.get(cache_channel_key)
        if not channel_online_users:
            return

        try:
            channel_online_users.remove(user_id)
        except KeyError:
            return

        cache.set(cache_channel_key, channel_online_users)
        emit("userDisconnectedResponse", list(channel_online_users), broadcast=True)

    return socketio
