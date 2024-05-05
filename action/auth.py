from enum import Enum
from dto.auth import AuthData, CheckLogin, RegisterData, JwtData, Role
from passlib.hash import sha512_crypt
import time
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
        service_card = self.DB_manager.find_account(userdata.username)  # (service_data_login, service_data_password, service_data_role, service_data_id)
        client_card = self.DB_manager.get_client(service_card[-1])

        if not service_card:
            print(f"No such user: {userdata.username}")
            return None, AuthResult.NotFound

        if not sha512_crypt.verify(userdata.password, service_card[1]):
            print(f"Wrong Password for user {userdata.username}")
            return None, AuthResult.WrongData

        print(f"Auth Success for user {userdata.username}")
        return self.gen_jwt(service_card[0], service_card[2], client_card[0]), AuthResult.Accept

    @staticmethod
    def gen_jwt(username, role, user_id) -> str:
        jwt_token = jwt.encode({"username": username, "date": round(time.time()), "role": role, "id": user_id},
                               JWT_SECRET, algorithm="HS256")
        return jwt_token

    def check_jwt(self, jwt_token) -> (JwtData, JwtCheckResult):
        try:
            jwt_data = jwt.decode(jwt_token, JWT_SECRET, algorithms=["HS256"])
        except jwt.exceptions.InvalidSignatureError:
            return None, JwtCheckResult.BadSignature

        try:
            #print(jwt_data)
            jwt_data = JwtData(jwt_data)
        except ValueError:
            return None, JwtCheckResult.BadFields
        now = time.time()

        if not (0 < now - jwt_data.date < 86400):
            self.drop_session(jwt_token)
            return None, JwtCheckResult.Expired

        return jwt_data, JwtCheckResult.Verified

    def check_login_exists(self, userdata: [CheckLogin, RegisterData]):
        user_card = self.DB_manager.find_account(userdata.username)
        print(f"Verified user {userdata.username} existence with result {bool(user_card)}")
        return bool(user_card)

    def register(self, userdata: RegisterData):
        if not self.check_login_exists(userdata):
            self.DB_manager.create_service_data(userdata)
            if userdata.role == Role.Master:
                self.DB_manager.create_master_profile(userdata)
            else:
                self.DB_manager.create_client_profile(userdata)
            return RegisterResult.Accept
        return RegisterResult.Decline

    def drop_session(self, jwt_token):
        pass
