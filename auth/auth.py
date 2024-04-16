from enum import Enum

from passlib.hash import sha512_crypt
from datetime import datetime
import jwt

from config import JWT_SECRET
from db.db_manager import DataBaseManager


class AuthResult(Enum):
    NotFound = 1
    WrongData = 2
    Accept = 3


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager
        pass

    def login(self, userdata) -> AuthResult:
        username = userdata["username"]
        password = userdata["password"]
        user_card = self.DB_manager.find_account(username)  # (login, pass, auth_id)

        if not user_card:
            return AuthResult.NotFound

        if not sha512_crypt.verify(password, user_card[1]):
            return AuthResult.WrongData

        return AuthResult.Accept

    @staticmethod
    def gen_jwt(username, role) -> str:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y-%H:%M:%S")
        jwt_token = jwt.encode({"username": username, "date": dt_string, "role": role}, JWT_SECRET, algorithm="HS256")
        return jwt_token

    def register(self, userdata):
        username = userdata["username"]
        role = userdata["role"]
        password = sha512_crypt.hash(userdata["password"])
        self.DB_manager.create_service_data(username, password, role)

