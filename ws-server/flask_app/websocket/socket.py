from flask_socketio import SocketIO

socketio = SocketIO(logger=True, engineio_logger=True, cors_allowed_origins="*")
# socketio = SocketIO(async_mode='eventlet', logger=True, engineio_logger=True, cors_allowed_origins="*", message_queue="redis://redis:6379/0")
