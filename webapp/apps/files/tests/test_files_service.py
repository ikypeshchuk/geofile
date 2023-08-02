from unittest import mock

from freezegun import freeze_time
from requests import Response

from app import create_app
from apps.files.services.file_services import FilesService
from py_helpers.tests.base_test import BaseTestCase


class TestFilesService(BaseTestCase):
    @staticmethod
    def mocked_requests_get(*args, **kwargs):
        response = Response()
        response.status_code = 200
        file_content = b'test file content'
        response._content = file_content
        return response

    @staticmethod
    def mocked_get_location(*args, **kwargs):
        return {
            'ip': '0.0.0.0',
            'city': 'Hesse',
            'region': 'Frankfurt am Main',
            'country': 'DE'
        }

    @staticmethod
    def mocked_list_objects(*args, **kwargs):
        return {
            'Contents': [
                {'Key': f'{i}.txt', 'Size': 1024}
                for i in range(10)
            ]
        }

    @mock.patch('boto3.client')
    def setUp(self, mock_boto_client):
        self.s3_mock = mock.MagicMock()
        mock_boto_client.return_value = self.s3_mock

        self.s3_mock.head_object.return_value = {'ContentLength': 1024}
        self.s3_mock.list_objects.return_value = self.mocked_list_objects()
        self.s3_mock.get_object.return_value = {'Body': 'mock_file_stream'}

        self.files_service = FilesService(url='http://example.com/file.txt')
        self.app, _ = create_app()

    def test_get_filename(self):
        self.assertEqual(self.files_service.get_filename(), 'file.txt')

    def test_get_file_extension(self):
        self.assertEqual(self.files_service.get_file_extension(), '.txt')

    @freeze_time('Jul 31st, 2023')
    @mock.patch('apps.files.services.ip_address_services.IpAddress.get_location', side_effect=mocked_get_location)
    @mock.patch('apps.files.services.file_services.uuid4', return_value='9be7d5d6-6067-44f5-a672-9076af5ec117')
    @mock.patch('apps.files.services.file_services.cache.set', return_value=None)
    @mock.patch('apps.files.services.file_services.requests.get', side_effect=mocked_requests_get)
    def test_upload_to_s3(self, mock_requests_get, mock_cache_set, mock_uuid4, mock_get_location):
        with self.app.app_context():

            data = self.files_service.upload_to_s3()
            self.assertEqualFixture(data, 'fixtures/services/files_service_upload_to_s3.json')

        self.s3_mock.upload_fileobj.assert_called_once()
        self.s3_mock.head_object.assert_called_once()
        mock_cache_set.assert_called_once()
        mock_requests_get.assert_called_once()
        mock_uuid4.assert_called_once()
        mock_get_location.assert_called_once()

    @freeze_time('Jul 31st, 2023')
    @mock.patch('apps.files.services.ip_address_services.IpAddress.get_location', side_effect=mocked_get_location)
    @mock.patch('apps.files.services.file_services.uuid4', return_value='9be7d5d6-6067-44f5-a672-9076af5ec117')
    def test_file_replication(self, mock_uuid4, mock_get_location):
        with self.app.app_context():

            data = self.files_service.file_replication(self.files_service.get_new_filename())
            self.assertEqualFixture(data, 'fixtures/services/files_service_file_replication.json')

        self.s3_mock.copy.assert_called_once()
        mock_uuid4.assert_called_once()
        mock_get_location.assert_called_once()

    @mock.patch('apps.files.services.ip_address_services.IpAddress.get_location', side_effect=mocked_get_location)
    def test_list_files(self, mock_get_location):
        with self.app.app_context():

            data = self.files_service.list_files()
            self.assertEqualFixture(data, 'fixtures/services/files_service_list_files.json')

        self.s3_mock.list_objects.assert_called_once()
        mock_get_location.assert_called()
        assert mock_get_location.call_count == len(self.mocked_list_objects()['Contents'])

    @mock.patch('apps.files.services.file_services.cache.get', return_value=None)
    @mock.patch('apps.files.services.file_services.cache.delete', return_value=None)
    def test_delete_file(self, mock_cache_get, mock_cache_delete):
        with self.app.app_context():

            self.files_service.delete_file(self.files_service.get_filename())

        self.s3_mock.delete_object.assert_called_once()
        mock_cache_get.assert_called_once()
        mock_cache_delete.assert_called_once()

    def test_get_file_stream_from_s3(self):
        with self.app.app_context():

            self.files_service.get_file_stream_from_s3(self.files_service.get_filename())

        self.s3_mock.get_object.assert_called_once()
