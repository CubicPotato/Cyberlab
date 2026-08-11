import os
import unittest

from api import create_app


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        os.environ["DB_USER"] = "postgres"
        os.environ["DB_PASSWORD"] = "password"
        os.environ["DB_HOST"] = "localhost"
        os.environ["DB_PORT"] = "5432"
        os.environ["DB_NAME"] = "postgres"

    def test_protected_route_accepts_valid_basic_auth(self):
        app = create_app()
        client = app.test_client()

        response = client.get(
            "/api/me",
            auth=("admin", "12345"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"login": "admin"})

    def test_protected_route_rejects_invalid_basic_auth(self):
        app = create_app()
        client = app.test_client()

        response = client.get(
            "/api/me",
            auth=("admin", "wrong-password"),
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
