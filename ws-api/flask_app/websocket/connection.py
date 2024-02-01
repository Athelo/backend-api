import requests
from flask import request, current_app as app
from flask_socketio import emit, Namespace

from flask_app.websocket.socket import socketio
from flask_app.cache import cache
from flask_app.utils.middleware import websocket_jwt_authenticated


class MyCustomNamespace(Namespace):
    def on_connect(self):
        print(f"Client connected - {request.sid}")
        emit("connectResponse", {request.sid})

    def on_sign_in(self, data):
        print(f"Client signed in - {request.sid}")
        emit("signInResponse", data)

    def on_join_message_channel(self, data):
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

    @websocket_jwt_authenticated
    def on_message(self, data):
        print("Client message")
        message_channel_id = int(data.get("messageChannelId"))
        sender_name = data.get("senderName")
        content = data.get("text")

        response = requests.post(
            f"{app.config.get('REST_API_SERVER_URL')}/api/v1/message-channels/{message_channel_id}/messages/", json={
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

    @websocket_jwt_authenticated
    def on_typing(self, data):
        print("Client typing")
        emit("typingResponse", data, broadcast=True)

    def on_disconnect(self):
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


@socketio.on_error('/chat')
def error_handler_chat(e):
    pass


socketio.on_namespace(MyCustomNamespace('/chat'))
