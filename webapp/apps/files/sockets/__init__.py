from socket import SocketIO

from apps.files.sockets.views import disconnect, connect


def init_socketio_views(socketio: SocketIO) -> None:
    socketio.on_event('connect', connect)
    socketio.on_event('disconnect', disconnect)
