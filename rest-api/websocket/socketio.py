from flask_socketio import SocketIO


# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = "eventlet"
socketio = SocketIO(async_mode=async_mode, logger=True, engineio_logger=True)
