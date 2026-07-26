from .extension import db

class User(db.Model):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    login = db.Column(db.String(120), unique=True)

    password = db.Column(db.String(255))

    def bdcheck(self, pw) -> bool:
        return pw == self.password