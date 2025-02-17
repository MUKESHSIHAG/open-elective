from flask_login import UserMixin
# from db import get_db

class User(UserMixin):
    def __init__(self, id_, name, email, roll_number, branch, branch_code, semester, cgpi):
        self.id = id_
        self.name = name
        self.email = email
        self.roll_number = roll_number
        self.branch = branch
        self.branch_code = branch_code
        self.semester = semester
        self.cgpi = cgpi

    @staticmethod
    def get(user_id):
        conn = get_db()
        db = conn.cursor()
        db.execute(
            "SELECT * FROM users WHERE id = (%s)", (user_id,)
        )
        user = db.fetchone()
        if not user:
            return None

        user = User(
            id_=user[0], name=user[1], email=user[2], roll_number=user[3], branch=user[4], branch_code=user[5], semester=user[6], cgpi=user[7]
        )
        return user

    @staticmethod
    def create(id_, name, email, roll_number, branch, branch_code, semester, cgpi):
        # with get_db() as conn:
        #     with 
        conn = get_db()
        db = conn.cursor()
        db.execute(
            "INSERT INTO users (id, name, email, roll_number, branch, branch_code, semester, cgpi) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
            (id_, name, email, roll_number, branch, branch_code, semester, cgpi),
        )
        conn.commit()

from app import get_db