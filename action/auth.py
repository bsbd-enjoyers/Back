from enum import Enum
from dto.auth import AuthData, CheckLogin, RegisterData, JwtData, Role, ServiceData
from passlib.hash import sha512_crypt
from db.db_manager import QueryResult
import time
import jwt

from config import JWT_SECRET
from db.db_manager import DataBaseManager


class AuthResult(Enum):
    NotFound = 1
    WrongPassword = 2
    Accept = 3
    Banned = 4


class RegisterResult(Enum):
    Accept = 1
    Decline = 2


class JwtCheckResult(Enum):
    Expired = 1
    BadSignature = 2
    Verified = 3
    BadFields = 4


class CheckLoginResult(Enum):
    true = True
    false = False


class CheckPermission(Enum):
    BadPermissions = "Bad permissions"


class ReturnType(Enum):
    TwoVal = 2
    OneVal = 1


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager

    def login(self, userdata: AuthData):
        service_card, search_res = self.DB_manager.find_account(userdata.username)

        if search_res == QueryResult.Fail:
            return None, search_res

        if not service_card:
            print(f"No such user: {userdata.username}")
            return None, AuthResult.NotFound

        service_data = ServiceData(service_card)
        if service_data.banned:
            return None, AuthResult.Banned

        if service_data.role == Role.Master:
            user_card, search_res = self.DB_manager.get_master(userdata.username)
            user_card = user_card[0]
        elif service_data.role == Role.Client:
            user_card, search_res = self.DB_manager.get_client(userdata.username)
            user_card = user_card[0]
        else:
            user_card = 0

        if search_res == QueryResult.Fail:
            return None, search_res

        if not sha512_crypt.verify(userdata.password, service_card[1]):
            return None, AuthResult.WrongPassword

        return self.__gen_jwt(service_data.login, service_data.role.value, user_card), AuthResult.Accept

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
            return result
        return CheckLoginResult(bool(user_card))

    def register(self, userdata: RegisterData):
        if userdata.role == Role.Admin:
            return RegisterResult.Decline
        if self.check_login_exists(userdata) == CheckLoginResult.true:
            return RegisterResult.Decline
        if self.DB_manager.create_account(userdata)[-1] == QueryResult.Success:
            return RegisterResult.Accept
        return RegisterResult.Decline

    @staticmethod
    def check_permissions_factory(permissions: list, return_type: ReturnType):
        def check_permissions(fun):
            def wrapper(self, entity):
                if type(entity) is not JwtData:
                    if entity.jwt_data.role in permissions:
                        return fun(self, entity)
                else:
                    if entity.role in permissions:
                        return fun(self, entity)

                if return_type == ReturnType.TwoVal:
                    return None, CheckPermission.BadPermissions
                return CheckPermission.BadPermissions
            return wrapper
        return check_permissions

    def drop_session(self, jwt_token):
        pass
