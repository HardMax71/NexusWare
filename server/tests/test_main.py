# /server/tests/test_main.py
import unittest

from fastapi.testclient import TestClient

from server.app.main import app


class TestMain(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_root(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "Welcome to NexusWare WMS API"})


if __name__ == "__main__":
    unittest.main()
