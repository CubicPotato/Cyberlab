import os
import unittest
import requests
import psycopg

from app.api import create_app
from app.api.extension import db
from app.api.models import User


class LoginRouteTests(unittest.TestCase):
    def setUp(self):
        # Mode par défaut: local (utilise sqlite en mémoire)
        self.mode = os.getenv("TEST_TARGET", "local")
        self.base_url = os.getenv("PROD_BASE_URL", "http://localhost:8080")

        if self.mode == "local":
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
        else:
            # Ensure Postgres has the users table and admin user
            db_user = os.getenv("DB_USER", "postgres")
            db_password = os.getenv("DB_PASSWORD", "password")
            db_host = os.getenv("DB_HOST", "localhost")
            db_port = os.getenv("DB_PORT", "5432")
            db_name = os.getenv("DB_NAME", "postgres")

            conn = psycopg.connect(dbname=db_name, user=db_user, password=db_password, host=db_host, port=db_port)
            cur = conn.cursor()
            cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                login VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            ''')
            cur.execute("INSERT INTO users (login, password) VALUES ('admin', '12345') ON CONFLICT (login) DO NOTHING;")
            conn.commit()
            cur.close()
            conn.close()

    def tearDown(self):
        if self.mode == "local":
            db.session.remove()
            db.drop_all()
            self.app_context.pop()

    def test_login_accepts_valid_credentials(self):
        if self.mode == "prod":
            resp = requests.post(f"{self.base_url}/api/login", json={"login": "admin", "password": "12345"})
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["login"], "admin")
            return

        response = self.client.post(
            "/api/login",
            json={"login": "admin", "password": "12345"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["login"], "admin")

    def test_login_rejects_invalid_credentials(self):
        if self.mode == "prod":
            resp = requests.post(f"{self.base_url}/api/login", json={"login": "admin", "password": "wrong"})
            self.assertEqual(resp.status_code, 401)
            return

        response = self.client.post(
            "/api/login",
            json={"login": "admin", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
