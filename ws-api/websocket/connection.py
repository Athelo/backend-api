import requests
from flask import request, current_app as app
from flask_socketio import Namespace

from websocket.socket import socketio
from cache import cache
from utils.middleware import websocket_jwt_authenticated


class ChatNamespace(Namespace):
    def on_connect(self):
        print(f"Client connected - {request.sid}")
        self.emit("connectResponse", {"sessionId": request.sid})

    def on_sign_in(self, data):
        print(f"Client signed in - {request.sid}")
        self.emit("signInResponse", data)

    def on_join_message_channel(self, data):
        session_id = request.sid
        print(f"Client joined a message channel - {session_id}")
        user_id = int(data.get("userId"))
        message_channel_id = int(data.get("messageChannelId"))
        cache_channel_key = f"message_channel_{message_channel_id}"

        cache.set(f"user_session_{session_id}", f"{user_id}:{message_channel_id}")
        channel_online_users = cache.get(cache_channel_key)
        if not channel_online_users:
            channel_online_users = set()

        channel_online_users.add(user_id)
        channel_online_users = set(channel_online_users)
        cache.set(cache_channel_key, channel_online_users)
        self.emit("joinMessageChannelResponse", list(channel_online_users))

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
        self.emit("messageResponse", new_msg)

    @websocket_jwt_authenticated
    def on_typing(self, data):
        print("Client typing")
        self.emit("typingResponse", data)

    def on_disconnect(self):
        session_id = request.sid
        print(f"Client disconnected - {session_id}")
        user_session = cache.get(f"user_session_{session_id}")
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
        self.emit("userDisconnectedResponse", list(channel_online_users))
        self.disconnect(session_id)


socketio.on_namespace(ChatNamespace('/chat'))


@socketio.on_error('/chat')
def error_handler_chat(e):
    print(f"An error occurred========================: {e}")
