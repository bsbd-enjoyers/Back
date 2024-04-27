from enum import Enum
from dto.auth import AuthData, CheckLogin, RegisterData, JwtData
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


class JwtCheckResult(Enum):
    Expired = 1
    BadSignature = 2
    Verified = 3
    BadFields = 4


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager
        pass

    def login(self, userdata: AuthData):
        user_card = self.DB_manager.find_account(userdata.username)  # (login, pass, auth_id)

        if not user_card:
            print(f"No such user: {userdata.username}")
            return None, AuthResult.NotFound

        if not sha512_crypt.verify(userdata.password, user_card[1]):
            print(f"Wrong Password for user {userdata.username}")
            return None, AuthResult.WrongData

        print(f"Auth Success for user {userdata.username}")
        return self.gen_jwt(user_card[0], user_card[2]), AuthResult.Accept

    @staticmethod
    def gen_jwt(username, role) -> str:
        now = datetime.now()
        date_string = now.strftime("%d/%m/%Y/%H/%M/%S")
        jwt_token = jwt.encode({"username": username, "date": date_string, "role": role}, JWT_SECRET, algorithm="HS256")
        return jwt_token

    @staticmethod
    def check_jwt(jwt_token):
        try:
            jwt_data = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            return None, JwtCheckResult.BadSignature

        try:
            #print(jwt_data)
            jwt_data = JwtData(jwt_data)
        except ValueError:
            return None, JwtCheckResult.BadFields

        date = datetime.strptime(jwt_data.date, "%d/%m/%Y/%H/%M/%S")  # TODO: CHECK DATE
        return jwt_data, JwtCheckResult.Verified

    def check_login_exists(self, userdata: [CheckLogin, RegisterData]):
        user_card = self.DB_manager.find_account(userdata.username)
        print(f"Verified user {userdata.username} existence with result {bool(user_card)}")
        return bool(user_card)

    def register(self, userdata: RegisterData):
        if not self.check_login_exists(userdata):
            self.DB_manager.create_service_data(userdata)
            if userdata.role == "master":
                self.DB_manager.create_master_profile(userdata)
            else:
                self.DB_manager.create_client_profile(userdata)
            return RegisterResult.Accept
        return RegisterResult.Decline
