from flask_login import UserMixin
from db import get_db

class User(UserMixin):
    def __init__(self, id_, name, email, roll_number, branch, semester, cgpi):
        self.id = id_
        self.name = name
        self.email = email
        self.roll_number = roll_number
        self.branch = branch
        self.semester = semester
        self.cgpi = cgpi

    @staticmethod
    def get(user_id):
        db = get_db()
        user = db.execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], roll_number=user[3], branch=user[4], semester=user[5], cgpi=user[6]
        )
        return user

    @staticmethod
    def create(id_, name, email, roll_number, branch, semester, cgpi):
        db = get_db()
        db.execute(
            "INSERT INTO user (id, name, email, roll_number, branch, semester, cgpi) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (id_, name, email, roll_number, branch, semester, cgpi),
        )
        db.commit()