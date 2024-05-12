from dto.prototypes import ResponsePrototype
from dto.auth import Role
from flask import jsonify


class UserInfo(ResponsePrototype):
    def __init__(self, user_info_tuple):
        self.id = user_info_tuple[0]
        self.fullname = user_info_tuple[1]
        self.email = user_info_tuple[2]
        self.phone = user_info_tuple[3]
        self.login = user_info_tuple[4]
        self.role = "client"
        if len(user_info_tuple) == 6:
            self.about_me = user_info_tuple[5]
            self.role = "master"
            self.skills = dict()

    def add_skills(self, skill_tuple):
        if self.role == "client":
            return

        for skill in skill_tuple:
            self.skills[skill[0]] = skill[1]

    def response(self):
        if self.role == "master" and not self.skills:
            raise ValueError(f"Empty skills for master {self.fullname}")
        self.__dict__.pop('id')
        return jsonify(self.__dict__)

    def get_dict(self):
        self.__dict__.pop('id')
        return self.__dict__


class MasterInfo(ResponsePrototype):
    def __init__(self, master_card):
        self.fullname = master_card[0]
        self.email = master_card[1]
        self.phone = master_card[2]
        self.about_me = master_card[3]
        self.role = "master"
        self.skills = dict()
        self.score = None

    def add_skills(self, skill_tuple):
        for skill in skill_tuple:
            self.skills[skill[0]] = skill[1]

    def add_score(self, score):
        self.score = 0 if score is None else float(score)


class Users(ResponsePrototype):
    def __init__(self, user_cards):
        self.users = [UserInfo(user_info).get_dict() for user_info in user_cards]
