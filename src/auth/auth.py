import jwt, crypt, datetime
from enum import Enum
from db.db_manager import DBmanager
from config import JWT_SECRET

class AuthResult(Enum):
    NotFound=1
    WrongData=2
    Accept=3

class Auth:
    def __init__(self, dbmanager: DBmanager) -> None:
        self.DBmanager = dbmanager
        pass

    def login(self, userdata):
        username = userdata["username"]
        password = userdata["password"]
        user_card = self.DBmanager.find_login(username) # (login, pass, auth_id)
        
        if not user_card:
            return AuthResult.NotFound

        if not crypt.crypt(password, user_card[1]) == user_card[1]:
            return AuthResult.WrongData

        return AuthResult.Accept
    
    def gen_jwt(self, username):
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y-%H:%M:%S")
        jwttoken = jwt.encode({"username": username, "date": dt_string}, JWT_SECRET, algorithm="HS256")
        return jwttoken
    
    def register(self, userinfo):
