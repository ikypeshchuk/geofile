from uuid import uuid4

from flask import request
from flask_socketio import emit

from cache import cache


def connect():
    user_sid = request.cookies.get('userSID')
    if not user_sid:
        user_sid = str(uuid4())
        emit('setUserSID', user_sid)

    cache.delete(user_sid)
    cache.add(user_sid, request.sid)


def disconnect():
    user_sid = request.cookies['userSID']
    cache.delete(user_sid)
