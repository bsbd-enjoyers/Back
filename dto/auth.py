from dto.prototypes import DataPrototype
from passlib.hash import sha512_crypt


class AuthData(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.password = userdata.get("password")
        self.check_empty()


class RegisterData(DataPrototype):
    def __init__(self, userdata):
        self.service_data_id = "empty"
        self.username = userdata.get("login")
        self.password = userdata.get("password")
        self.fullname = userdata.get("fullname")
        self.role = userdata.get("role")
        self.email = userdata.get("email")
        self.phone = userdata.get("phone")
        if self.role == "master":
            self.skills = userdata.get("skills")
            self.about = userdata.get("")
        self.check_empty()
        self.password = sha512_crypt.hash(self.password)

    def add_service_data_id(self, service_data_id: int):
        self.service_data_id = service_data_id


class CheckLogin(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.check_empty()


class JwtData(DataPrototype):
    def __init__(self, jwt_dict):
        self.username = jwt_dict.get("username")
        self.date = jwt_dict.get("date")
        self.role = jwt_dict.get("role")
        self.check_empty()
