from gevent import monkey

monkey.patch_all()


from app import create_app


flask_app, socketio = create_app()


if __name__ == '__main__':
    socketio.run(flask_app, host='0.0.0.0', port=8008, debug=True, allow_unsafe_werkzeug=True)
