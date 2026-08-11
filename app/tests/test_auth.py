import os
import unittest
import requests
from requests.auth import HTTPBasicAuth

try:
    import psycopg
except ImportError:  # pragma: no cover - exercised in local runs without psycopg
    psycopg = None

from app.api import create_app


def _connect_postgres():
    if psycopg is None:
        raise RuntimeError("psycopg is required for prod-mode tests")

    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "password")
    db_port = int(os.getenv("DB_PORT", "5432"))
    db_name = os.getenv("DB_NAME", "postgres")

    hosts = [os.getenv("DB_HOST"), "127.0.0.1", "localhost"]
    last_error = None
    for host in hosts:
        if not host:
            continue
        try:
            conn = psycopg.connect(dbname=db_name, user=db_user, password=db_password, host=host, port=db_port)
            return conn
        except Exception as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise RuntimeError("Unable to connect to PostgreSQL")


class AuthFlowTests(unittest.TestCase):
    def setUp(self):
        # Mode: 'local' (default) uses Flask test_client; 'prod' uses real HTTP against PROD_BASE_URL
        self.mode = os.getenv("TEST_TARGET", "local")
        self.base_url = os.getenv("PROD_BASE_URL", "http://localhost:8080")

        # If testing against Postgres, ensure the users table and admin user exist
        if self.mode == "prod":
            conn = _connect_postgres()
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

    def test_protected_route_accepts_valid_basic_auth(self):
        if self.mode == "prod":
            resp = requests.get(f"{self.base_url}/api/me", auth=HTTPBasicAuth("admin", "12345"))
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json(), {"login": "admin"})
            return

        app = create_app()
        client = app.test_client()
        response = client.get(
            "/api/me",
            auth=("admin", "12345"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json(), {"login": "admin"})

    def test_protected_route_rejects_invalid_basic_auth(self):
        if self.mode == "prod":
            resp = requests.get(f"{self.base_url}/api/me", auth=HTTPBasicAuth("admin", "wrong-password"))
            self.assertEqual(resp.status_code, 401)
            return

        app = create_app()
        client = app.test_client()
        response = client.get(
            "/api/me",
            auth=("admin", "wrong-password"),
        )

        self.assertEqual(response.status_code, 401)


if __name__ == "__main__":
    unittest.main()
