import time
import os
from datetime import datetime
import pytz
from io import BytesIO
from typing import Dict, Union, Any
from uuid import uuid4

import boto3
import requests
from boto3.s3.transfer import TransferConfig
from flask import url_for

from apps.files.services.ip_address_services import IpAddress
from cache import cache
from config import Config


class FilesService:
    def __init__(self,
                 url: str = None,
                 s3_bucket_name: str = Config.AWS_S3_BUCKET_NAME,
                 ipaddress: str = Config.AWS_INSTANCE_IP) -> None:
        self.url = url
        self.s3_bucket_name = s3_bucket_name
        self.ipaddress = ipaddress
        self.s3 = boto3.client('s3')

    @classmethod
    def get_replica_buckets(cls) -> list:
        return [[serv.strip() for serv in obj.strip().split('::') if serv]
                for obj in Config.AWS_REPLICA_BUCKETS.split(',') if obj]

    def download_file(self) -> Dict:
        return self.upload_to_s3()

    def get_filename(self) -> str:
        return os.path.basename(self.url)

    def get_file_extension(self) -> str:
        _, ext = os.path.splitext(self.get_filename())
        return ext if ext else ''

    def get_new_filename(self) -> str:
        return f'{uuid4()}{self.get_file_extension()}'

    def make_file_data(self,
                       s3: Any,
                       filename: str,
                       origin_filename: str,
                       download_duration: Union[int, float],
                       created_at: str) -> Dict:
        response = s3.head_object(Bucket=self.s3_bucket_name, Key=filename)
        size = response['ContentLength']

        return {
            'created_at': created_at,
            'download_duration': f'{download_duration:.2f}',
            'download_url': str(url_for('files_bp.download', filename=filename)),
            'size': size,
            'filename': filename,
            'replica': False,
            'origin_filename': origin_filename,
            'location': IpAddress(self.ipaddress).get_location()
        }

    def _download_file_stream(self) -> BytesIO:
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        return BytesIO(response.content)

    def upload_to_s3(self) -> Dict:
        assert self.url

        filename = self.get_new_filename()

        with self._download_file_stream() as file_stream:
            start_time = time.time()
            self.s3.upload_fileobj(
                file_stream,
                self.s3_bucket_name,
                filename,
                Config=TransferConfig(use_threads=True, max_concurrency=4)
            )
            download_duration = time.time() - start_time
            created_at = str(datetime.now(pytz.timezone('UTC')))

            data = self.make_file_data(self.s3, filename, self.get_filename(), download_duration, created_at)
            cache.set(filename, data, timeout=((60*60)*24)*20)
            return data

    def file_replication(self, filename: str) -> Dict:
        copy_source = {
            'Bucket': Config.AWS_S3_BUCKET_NAME,
            'Key': filename
        }

        start_time = time.time()
        self.s3.copy(copy_source, self.s3_bucket_name, filename)
        download_duration = time.time() - start_time
        created_at = str(datetime.now(pytz.timezone('UTC')))

        data = self.make_file_data(self.s3, filename, filename, download_duration, created_at)
        data['replica'] = True

        return data

    def list_files(self) -> list:
        try:
            return [{'filename': item['Key'],
                     'location': IpAddress(self.ipaddress).get_location(),
                     'size': item['Size'],
                     'download_url': str(url_for('files_bp.download', filename=item['Key']))}
                    for item in self.s3.list_objects(Bucket=self.s3_bucket_name)['Contents']]
        except Exception as exc:
            return []

    def delete_file(self, filename: str) -> Dict:
        self.s3.delete_object(Bucket=self.s3_bucket_name, Key=filename)
        data = cache.get(filename)
        cache.delete(filename)
        return data or {}

    def get_file_stream_from_s3(self, filename):
        response = self.s3.get_object(Bucket=self.s3_bucket_name, Key=filename)
        file_stream = response['Body']
        return file_stream
