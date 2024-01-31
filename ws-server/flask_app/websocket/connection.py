import requests
from flask import request
from flask_socketio import emit

from flask_app.websocket.socket import socketio
from flask_app.cache import cache
from flask_app.utils.middleware import websocket_jwt_authenticated


@socketio.on("connect")
def connect(data):
    print(f"Client connected - {request.sid}")
    emit("connectResponse", data)


@socketio.on("sign_in")
def join(data):
    print(f"Client signed in - {request.sid}")
    emit("signInResponse", data)


@socketio.on("join_message_channel")
def join(data):
    print(f"Client joined a message channel - {request.sid}")
    user_id = int(data.get("userId"))
    message_channel_id = int(data.get("messageChannelId"))
    cache_channel_key = f"message_channel_{message_channel_id}"

    cache.set(f"user_session_{request.sid}", f"{user_id}:{message_channel_id}")
    channel_online_users = cache.get(cache_channel_key)
    if not channel_online_users:
        channel_online_users = set()

    channel_online_users.add(user_id)
    channel_online_users = set(channel_online_users)
    cache.set(cache_channel_key, channel_online_users)
    emit("joinMessageChannelResponse", list(channel_online_users), broadcast=True)


@socketio.on("message")
@websocket_jwt_authenticated
def message(data):
    print("Client message")
    message_channel_id = int(data.get("messageChannelId"))
    sender_name = data.get("senderName")
    content = data.get("text")

    response = requests.post(f"http://athelo-backend-api:8080/api/v1/message-channels/{message_channel_id}/messages/", json={
        "content": content
    }, headers={
        "Authorization": f"Bearer {request.main_token}"
    })

    msg = response.json()

    new_msg = {
        "id": msg["id"],
        "sender": sender_name,
        "text": content,
        "time": msg["created_at"]
    }
    emit("messageResponse", new_msg, broadcast=True)


@socketio.on("typing")
# @websocket_jwt_authenticated
def typing(data):
    print("Client typing")
    emit("typingResponse", data, broadcast=True)


@socketio.on("disconnect")
def disconnect():
    print(f"Client disconnected - {request.sid}")
    user_session = cache.get(f"user_session_{request.sid}")
    if not user_session:
        return

    user_id, message_channel_id = tuple(user_session.split(":"))
    user_id = int(user_id)
    message_channel_id = int(message_channel_id)
    cache_channel_key = f"message_channel_{message_channel_id}"

    channel_online_users = cache.get(cache_channel_key)
    channel_online_users = set(channel_online_users)
    if not channel_online_users:
        return

    try:
        channel_online_users.remove(user_id)
    except KeyError:
        return

    cache.set(cache_channel_key, channel_online_users)
    emit("userDisconnectedResponse", list(channel_online_users), broadcast=True)

