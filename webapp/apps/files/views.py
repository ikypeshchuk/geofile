import os
from io import BytesIO

from flask import Blueprint, send_file, render_template, jsonify, request
from marshmallow import ValidationError

from apps.files.schemas import FileUploadSchema
from apps.files.services.file_services import FilesService
from apps.files.services.ip_address_services import IpAddress
from apps.files.tasks import download_file, delete_replication_file
from config import Config


files_bp = Blueprint(
    'files_bp',
    __name__,
    template_folder='templates'
)


@files_bp.route('/', methods=['GET'])
def home():
    data = {
        'location': IpAddress(Config.AWS_INSTANCE_IP).get_location()
    }
    return render_template('home.html', **data)


@files_bp.route('/upload', methods=['POST'])
def upload():
    request_data = request.json
    schema = FileUploadSchema()
    try:
        validate_data = schema.load(request_data)
        download_file.delay(validate_data['url'], request.cookies['userSID'])
    except ValidationError as err:
        return jsonify(err.messages), 400
    return jsonify({'success': True})


@files_bp.route('/list-files')
def list_files():
    return jsonify(FilesService().list_files())


@files_bp.route('/test-download')
def test_download():
    data = BytesIO(os.urandom(500 * 1024))
    return send_file(data, mimetype='image/jpeg', as_attachment=True, download_name='test.jpg', max_age=0)


@files_bp.route('/download/<string:filename>')
def download(filename: str):
    file_stream = FilesService().get_file_stream_from_s3(filename)
    return send_file(file_stream, as_attachment=True, download_name=filename)


@files_bp.route('/delete/<string:filename>', methods=['DELETE'])
def delete(filename: str):
    try:
        FilesService().delete_file(filename)

        for bucket in FilesService.get_replica_buckets():
            delete_replication_file.delay(filename, request.cookies['userSID'], bucket)

    except ValidationError as err:
        return jsonify(err.messages), 400
    return jsonify(), 204
