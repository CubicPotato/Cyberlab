import os
import unittest

from app import create_app


class ConfigValidationTests(unittest.TestCase):
    def setUp(self):
        self.previous_values = {name: os.environ.get(name) for name in ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")}
        for name in self.previous_values:
            os.environ.pop(name, None)

    def tearDown(self):
        for name, value in self.previous_values.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value

    def test_create_app_raises_when_db_env_is_missing(self):
        with self.assertRaises(RuntimeError):
            create_app()


if __name__ == "__main__":
    unittest.main()
