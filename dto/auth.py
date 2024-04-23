from dto.prototypes import DataPrototype
from passlib.hash import sha512_crypt


class AuthData(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.password = userdata.get("password")
        self.check_empty()


class RegisterData(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.password = userdata.get("password")
        self.role = userdata.get("role")
        self.email = userdata.get("email")
        self.phone = userdata.get("phone")
        if self.role == "master":
            self.skills = userdata.get("skills")
            self.about = userdata.get("")
        self.check_empty()
        self.password = sha512_crypt(self.password)


class CheckLogin(DataPrototype):
    def __init__(self, userdata):
        self.username = userdata.get("login")
        self.check_empty()
