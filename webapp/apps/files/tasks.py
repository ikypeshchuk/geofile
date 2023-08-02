import sys
import traceback
from celery import shared_task

from apps.files.services.file_services import FilesService
from cache import cache


@shared_task(ignore_result=False)
def download_file(file_url: str, user_sid: str) -> None:
    from celery_app import socketio

    room = cache.get(user_sid)
    if room:
        try:
            file_data = FilesService(file_url).download_file()
            socketio.emit('fileUploadSuccessful', file_data, room=room)

            for bucket in FilesService.get_replica_buckets():
                file_replication.delay(file_data['filename'], user_sid, bucket)

        except Exception as exc:
            traceback.print_exc(file=sys.stdout)
            socketio.emit('errors', 'Something went wrong, please try again later.', room=room)


@shared_task(ignore_result=False)
def file_replication(filename: str, user_sid: str, bucket: list) -> None:
    from celery_app import socketio

    room = cache.get(user_sid)
    if room:
        try:
            file_data = FilesService(s3_bucket_name=bucket[0], aws_dns=bucket[1]).file_replication(filename)
            socketio.emit('fileUploadSuccessful', file_data, room=room)
        except Exception as exc:
            traceback.print_exc(file=sys.stdout)
            socketio.emit('errors', 'Something went wrong, please try again later.', room=room)


@shared_task(ignore_result=False)
def delete_replication_file(filename: str, user_sid: str, bucket: list = None) -> None:
    from celery_app import socketio

    room = cache.get(user_sid)
    if room:
        try:
            msg = 'File success deleted.'

            if bucket is not None:
                file_data = FilesService(s3_bucket_name=bucket[0], aws_dns=bucket[1]).delete_file(filename)
                msg = 'Replication file success deleted.'
            else:
                file_data = FilesService().delete_file(filename)

            replica = file_data.get('replica', False)
            socketio.emit('messageSuccess', {'msg': msg, 'data': {'filename': filename, 'replica': replica}}, room=room)
        except Exception as exc:
            traceback.print_exc(file=sys.stdout)
            socketio.emit('errors', 'Something went wrong with deleting the file, please try again later.', room=room)
