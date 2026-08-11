import os
from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from .extension import db, auth as http_auth
from .models import User

load_dotenv()

def create_app(test_config=None):
    # initialize app and db
    app = Flask(__name__, instance_relative_config=True)
    
    # create and configure the app
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql+psycopg://"
        f"{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    db.init_app(app)
    
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    @app.route('/app/login', methods=['POST'])
    def login():
        data = request.get_json(silent=True) or {}
        login = data.get('login')
        password = data.get('password')

        if not login or not password:
            return jsonify({"error": "missing credentials"}), 400

        user = db.session.execute(db.select(User).where(User.login == login)).scalar_one_or_none()
        if user is None or not user.bdcheck(password):
            return jsonify({"error": "invalid credentials"}), 401

        return jsonify({"login": user.login})

    @app.route('/app/me')
    @http_auth.login_required
    def me():
        return {"login": g.current_user.login}

    return app