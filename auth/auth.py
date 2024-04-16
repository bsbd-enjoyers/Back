import jwt, crypt, datetime
from enum import Enum
from db.db_manager import DataBaseManager
from config import JWT_SECRET


class AuthResult(Enum):
    NotFound = 1
    WrongData = 2
    Accept = 3


class Auth:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager
        pass

    def login(self, userdata):
        username = userdata["username"]
        password = userdata["password"]
        user_card = self.DB_manager.find_login(username)  # (login, pass, auth_id)

        if not user_card:
            return AuthResult.NotFound

        if not crypt.crypt(password, user_card[1]) == user_card[1]:
            return AuthResult.WrongData

        return AuthResult.Accept

    @staticmethod
    def gen_jwt(username):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y-%H:%M:%S")
        jwt_token = jwt.encode({"username": username, "date": dt_string}, JWT_SECRET, algorithm="HS256")
        return jwt_token

    def register(self, userinfo):
        pass
