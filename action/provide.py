from db.db_manager import DataBaseManager
from dto.auth import JwtData, Role
from dto.user import UserInfo
from dto.simple import Query
from dto.order import Orders


class Provide:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    def get_userinfo(self, jwt_data: JwtData) -> UserInfo:
        service_id = self.DB_manager.get_service_id(jwt_data.username)
        userinfo = None  # что будет если нет товарища в бд?
        print(jwt_data.role, service_id)
        if jwt_data.role == Role.Client:
            userinfo = self.DB_manager.get_client(service_id)
        elif jwt_data.role == Role.Master:
            userinfo = self.DB_manager.get_master(service_id)
            print(userinfo)

        userinfo = UserInfo(userinfo)

        if userinfo.role == "master":
            userinfo.add_skills(self.DB_manager.get_skills(userinfo.id))

        return userinfo

    def get_orders(self, jwt_data: JwtData) -> Orders:
        if jwt_data.role == Role.Client:
            orders = Orders(self.DB_manager.get_client_orders(jwt_data.id))
            return orders
        if jwt_data.role == Role.Master:
            return Orders(())

    def search(self, query: Query):
        pass