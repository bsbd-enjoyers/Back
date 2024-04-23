from enum import Enum
from dto.auth import AuthData, CheckLogin, RegisterData
from passlib.hash import sha512_crypt
from datetime import datetime
import jwt

from config import JWT_SECRET
from db.db_manager import DataBaseManager


class AuthResult(Enum):
    NotFound = 1
    WrongData = 2
    Accept = 3


class RegisterResult(Enum):
    Accept = 1
    Decline = 2


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager
        pass

    def login(self, userdata: AuthData) -> AuthResult:
        user_card = self.DB_manager.find_account(userdata.username)  # (login, pass, auth_id)

        if not user_card:
            print(f"No such user: {userdata.username}")
            return AuthResult.NotFound

        if not sha512_crypt.verify(userdata.password, user_card[1]):
            print(f"Wrong Password for user {userdata.username}")
            return AuthResult.WrongData

        print(f"Auth Success for user {userdata.username}")
        return AuthResult.Accept

    @staticmethod
    def gen_jwt(username, role) -> str:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y-%H:%M:%S")
        jwt_token = jwt.encode({"username": username, "date": dt_string, "role": role}, JWT_SECRET, algorithm="HS256")
        return jwt_token

    def check_login_exists(self, userdata: CheckLogin):
        user_card = self.DB_manager.find_account(userdata.username)
        print(f"Verified user {userdata.username} existence with result {bool(user_card)}")
        return bool(user_card)

    def register(self, userdata: RegisterData):
        self.DB_manager.create_service_data(userdata.username, userdata.password, userdata.role)
