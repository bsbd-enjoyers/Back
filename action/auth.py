from enum import Enum
from dto.auth import AuthData, CheckLogin, RegisterData, JwtData, Role
from passlib.hash import sha512_crypt
from db.db_manager import QueryResult
import time
import jwt

from config import JWT_SECRET
from db.db_manager import DataBaseManager


class AuthResult(Enum):
    NotFound = 1
    WrongData = 2
    Accept = 3
    error = 4


class RegisterResult(Enum):
    Accept = 1
    Decline = 2


class JwtCheckResult(Enum):
    Expired = 1
    BadSignature = 2
    Verified = 3
    BadFields = 4


class CheckLoginResult(Enum):
    true = 1
    false = 2
    error = 3


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager

    def login(self, userdata: AuthData):
        service_card, account_search_res = self.DB_manager.find_account(userdata.username)

        if account_search_res == QueryResult.Fail:
            return None, AuthResult.error

        if not service_card:
            print(f"No such user: {userdata.username}")
            return None, AuthResult.NotFound

        if service_card[2] == "master":
            user_card, search_res = self.DB_manager.get_master(userdata.username)
        else:
            user_card, search_res = self.DB_manager.get_client(userdata.username)

        if search_res == QueryResult.Fail:
            return None, AuthResult.error

        if not sha512_crypt.verify(userdata.password, service_card[1]):
            print(f"Wrong Password for user {userdata.username}")
            return None, AuthResult.WrongData

        print(f"Auth Success for user {userdata.username}")
        return self.__gen_jwt(service_card[0], service_card[2], user_card[0]), AuthResult.Accept

    @staticmethod
    def __gen_jwt(username, role, user_id) -> str:
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
        now = round(time.time())
        # print(f"Now {now}, JWT {jwt_data.date}, Res {now - jwt_data.date}")
        if not (0 <= now - jwt_data.date < 86400):
            self.drop_session(jwt_token)
            return None, JwtCheckResult.Expired

        return jwt_data, JwtCheckResult.Verified

    def check_login_exists(self, userdata: [CheckLogin, RegisterData]):
        user_card, result = self.DB_manager.find_account(userdata.username)
        if result == QueryResult.Fail:
            return CheckLoginResult.error
        if user_card:
            return CheckLoginResult.true
        return CheckLoginResult.false

    def register(self, userdata: RegisterData):
        if self.check_login_exists(userdata) == CheckLoginResult.true:
            return RegisterResult.Decline
        if self.DB_manager.create_account(userdata)[-1] == QueryResult.Success:
            return RegisterResult.Accept
        return RegisterResult.Decline

    def drop_session(self, jwt_token):
        pass
