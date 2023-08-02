from typing import Tuple

from celery import Celery, Task
from flask import Flask
from flask_socketio import SocketIO

from apps.files.sockets import init_socketio_views
from apps.middleware import set_user_cookie, load_data_to_request
from cache import cache


def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config['CELERY'])
    celery_app.set_default()
    app.extensions['celery'] = celery_app
    return celery_app


def create_app() -> Tuple[Flask, SocketIO]:
    from apps.files.views import files_bp

    app = Flask(__name__, template_folder='templates')
    app.config.from_object('config.Config')
    app.after_request(set_user_cookie)
    app.before_request(load_data_to_request)

    with app.app_context():
        cache.init_app(app)
        celery_init_app(app)

        socketio = SocketIO(app, message_queue=app.config['SOCKETIO_MESSAGE_QUEUE'], logger=True, engineio_logger=True)
        init_socketio_views(socketio)

        app.register_blueprint(files_bp)

        return app, socketio

