from .extension import db
from werkzeug.security import check_password_hash, generate_password_hash

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(255))

    def set_password(self, pw: str) -> None:
        self.password = generate_password_hash(pw)

    def check_password(self, pw: str) -> bool:
        if not self.password:
            return False
        if self.password.startswith("pbkdf2:") or self.password.startswith("scrypt:"):
            return check_password_hash(self.password, pw)
        return False

    def check_password_insecure(self, pw: str) -> bool:
        return pw == self.password