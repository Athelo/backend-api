from flask_socketio import SocketIO

socketio = SocketIO(logger=True, engineio_logger=True, cors_allowed_origins="*")
