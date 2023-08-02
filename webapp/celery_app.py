from app import create_app


flask_app, socketio = create_app()

app = flask_app.extensions['celery']
