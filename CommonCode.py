import string
import secrets
import sqlite3
from multiprocessing import Lock
from passlib.hash import pbkdf2_sha256


class DbTools:
    def __init__(self, db_name='db.sqlite'):
        self.DB_Name = db_name
        self.db = sqlite3.connect(self.DB_Name, check_same_thread=False)
        self.cur = self.db.cursor()
        self.lock = Lock()

    def write(self, q, val, do_commit=True, many=False):
        self.lock.acquire(True)
        if many:
            self.cur.executemany(q, val)
            last_row_id = None
        else:
            last_row_id = self.cur.execute(q, val).lastrowid
        if do_commit:
            self.db.commit()
        self.lock.release()
        return last_row_id

    def read(self, q, val=(), f_all=True):
        self.lock.acquire(True)
        if f_all:
            res = self.cur.execute(q).fetchall() if val == () else self.cur.execute(q, val).fetchall()
        else:
            res = self.cur.execute(q).fetchone() if val == () else self.cur.execute(q, val).fetchone()
        self.lock.release()
        return res


class AuthTools:
    @staticmethod
    def make_token():
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for i in range(50))

    @staticmethod
    def hash_password(password):
        return pbkdf2_sha256.hash(password)

    @staticmethod
    def password_hash_verify(password, pw_hash):
        return pbkdf2_sha256.verify(password, pw_hash)
