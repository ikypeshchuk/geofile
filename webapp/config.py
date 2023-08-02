import os


class Config:
    DEPLOYMENT_ENVIRONMENT = os.getenv('DEPLOYMENT_ENVIRONMENT', 'PROD')
    IS_PROD = DEPLOYMENT_ENVIRONMENT == 'PROD'
    IS_DEV = DEPLOYMENT_ENVIRONMENT == 'DEV'
    IS_TEST = DEPLOYMENT_ENVIRONMENT == 'TEST'
    
    FLASK_APP = os.getenv('FLASK_APP')
    FLASK_DEBUG = bool(os.getenv('FLASK_DEBUG', False))
    SECRET_KEY = os.getenv('SECRET_KEY')
    SERVER_NAME = os.getenv('SERVER_NAME')
    PREFERRED_URL_SCHEME = os.getenv('PREFERRED_URL_SCHEME', 'http')
    BASEDIR = os.path.abspath(os.path.dirname(__file__))

    SOCKETIO_MESSAGE_QUEUE = os.getenv('SOCKETIO_MESSAGE_QUEUE')
    IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')

    AWS_INSTANCE_IP = os.getenv('AWS_INSTANCE_IP')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
    AWS_S3_BUCKET_NAME = os.getenv('AWS_S3_BUCKET_NAME')
    AWS_REPLICA_BUCKETS = os.getenv('AWS_REPLICA_BUCKETS')

    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'

    CELERY = {
        'broker_url': os.getenv('CELERY_REDIS_URL'),
        'result_backend': os.getenv('CELERY_RESULT_BACKEND'),
        'task_ignore_result': bool(os.getenv('CELERY_TASK_IGNORE_RESULT', True)),
        'broker_connection_retry_on_startup': bool(os.getenv('CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP', True))
    }
    CACHE = {
        'CACHE_TYPE': 'RedisCache',
        'CACHE_REDIS_URL': os.getenv('CACHE_REDIS_URL')
    }
