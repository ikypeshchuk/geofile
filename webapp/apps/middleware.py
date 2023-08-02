from uuid import uuid4

from flask import request, g

from config import Config


def set_user_cookie(response):
    user_sid = request.cookies.get('userSID', None)
    if not user_sid:
        response.set_cookie('userSID', str(uuid4()))
    return response


def load_data_to_request():
    g.server_name = Config.SERVER_NAME
