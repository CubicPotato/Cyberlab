import os
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from .extension import db, auth as http_auth
from . import auth as auth_module
from .models import User

load_dotenv()

REQUIRED_DB_ENV_VARS = ("DB_USER", "DB_PASSWORD", "DB_HOST", "DB_PORT", "DB_NAME")


def _get_database_uri() -> str:
    missing = [name for name in REQUIRED_DB_ENV_VARS if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Missing required database environment variables: {', '.join(missing)}")
    return (
        f"postgresql+psycopg://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )


def create_app(test_config=None):
    # initialize app and db
    app = Flask(__name__, instance_relative_config=True)
    
    # create and configure the app
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = _get_database_uri()
    app.config["ALLOW_INSECURE_PLAINTEXT_AUTH"] = False
    db.init_app(app)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/api/login', methods=['POST'])
    def login():
        data = request.get_json(silent=True) or {}
        if not isinstance(data, dict):
            return jsonify({"error": "invalid payload"}), 400

        login = data.get('login')
        password = data.get('password')

        if not isinstance(login, str) or not isinstance(password, str):
            return jsonify({"error": "invalid credentials format"}), 400
        login = login.strip()
        if not login or not password:
            return jsonify({"error": "missing credentials"}), 400

        user = db.session.execute(db.select(User).where(User.login == login)).scalar_one_or_none()
        if user is None:
            return jsonify({"error": "invalid credentials"}), 401
        if app.config["ALLOW_INSECURE_PLAINTEXT_AUTH"]:
            is_valid = user.check_password_insecure(password)
        else:
            is_valid = user.check_password(password)
        if not is_valid:
            return jsonify({"error": "invalid credentials"}), 401

        return jsonify({"login": user.login})

    @app.route('/api/me')
    @http_auth.login_required
    def me():
        return {"login": g.current_user.login}

    return app