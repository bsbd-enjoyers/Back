from db.db_manager import DataBaseManager
from dto.auth import JwtData
from dto.user import UserInfo


class Provide:
    def __init__(self, dbmanager: DataBaseManager) -> None:
        self.DB_manager = dbmanager

    def get_userinfo(self, jwt_data: JwtData) -> UserInfo:
        service_id = self.DB_manager.get_service_id(jwt_data.username)
        userinfo = self.DB_manager.get_client(service_id) if jwt_data.role == "client" \
            else self.DB_manager.get_master(service_id)
        userinfo = UserInfo(userinfo)

        if userinfo.role == "master":
            userinfo.add_skills(self.DB_manager.get_skills(userinfo.id))

        return userinfo
