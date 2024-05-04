from dto.prototypes import DataPrototype
from passlib.hash import sha512_crypt
from enum import Enum


class Role(Enum):
    Master = "master"
    Client = "client"

    @staticmethod
    def get(value):
        try:
            role = Role(value)
        except ValueError:
            return None
        return role


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
        self.role = Role.get(userdata.get("role"))
        self.email = userdata.get("email")
        self.phone = userdata.get("phone")
        if self.role == Role.Master:
            self.skills = userdata.get("skills")
            self.about = userdata.get("about_me")
            self.master_id = "empty"
        self.check_empty()
        self.password = sha512_crypt.hash(self.password)

    def add_service_data_id(self, service_data_id: int):
        self.service_data_id = service_data_id

    def add_master_id(self, master_id: int):
        self.master_id = master_id

    def get_skill_tuples(self):
        if self.master_id == "empty":
            raise ValueError("Fill master_id")
        return [(self.master_id, skill_type, skill_desc) for skill_type, skill_desc in self.skills.items()]


class CheckLogin(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.check_empty()


class JwtData(DataPrototype):
    def __init__(self, jwt_dict):
        self.username = jwt_dict.get("username")
        self.date = jwt_dict.get("date")
        self.role = Role.get(jwt_dict.get("role"))
        self.check_empty()
