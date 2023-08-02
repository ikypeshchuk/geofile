import json
import unittest
from typing import Any

from config import Config


class BaseTestCase(unittest.TestCase):
    def assertEqualFixture(self, data: Any, path_to_fixture: str, export: bool = False) -> None:
        if export:
            self.save_fixture(data, path_to_fixture)
        fixture = self.load_json(path_to_fixture)
        self.assertEqual(data, fixture)

    def assertNoContent(self, response):
        self.assertEqual(response.status_code, 204)

    def assertOk(self, response):
        self.assertEqual(response.status_code, 200)

    def assertCreated(self, response):
        self.assertEqual(response.status_code, 201)

    @staticmethod
    def make_full_path(path: str) -> str:
        if not path.startswith('/'):
            path = f'/{path}'
        return f'{Config.BASEDIR}{path}'

    def save_fixture(self, data: Any, path: str) -> None:
        with open(self.make_full_path(path), 'w') as f:
            json.dump(data, f, indent=True)

    def load_json(self, path: str):
        with open(self.make_full_path(path), 'r') as f:
            return json.load(f)

