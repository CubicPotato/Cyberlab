import unittest

from app.api import create_app
from app.api.extension import db
from app.api.models import User


class LoginRouteTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        db.session.add(User(login="admin", password="12345"))
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_login_accepts_valid_credentials(self):
        response = self.client.post(
            "/api/login",
            json={"login": "admin", "password": "12345"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["login"], "admin")

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            "/api/login",
            json={"login": "admin", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
