import unittest

from app import create_app
from app.extension import db
from app.models import User


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        })
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        user = User(login="admin")
        user.set_password("12345")
        db.session.add(user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_protected_route_accepts_valid_basic_auth(self):
        response = self.client.get(
            "/api/me",
            auth=("admin", "12345"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"login": "admin"})

    def test_protected_route_rejects_invalid_basic_auth(self):
        response = self.client.get(
            "/api/me",
            auth=("admin", "wrong-password"),
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
