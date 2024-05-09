from db.db_manager import DataBaseManager, QueryResult
from dto.auth import JwtData, Role
from dto.user import UserInfo
from dto.simple import Query
from dto.order import Orders


class GetResult:
    Fail = 1
    Success = 2


class Provide:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    def get_userinfo(self, jwt_data: JwtData) -> (UserInfo, GetResult):

        if jwt_data.role == Role.Client:
            userinfo, result = self.DB_manager.get_client(jwt_data.username)
        else:
            userinfo, result = self.DB_manager.get_master(jwt_data.username)

        if result == QueryResult.Fail:
            return None, GetResult.Fail

        userinfo = UserInfo(userinfo)

        if userinfo.role == "master":
            skills, result = self.DB_manager.get_skills(userinfo.id)
            if result == QueryResult.Fail:
                return None, GetResult.Fail
            userinfo.add_skills(skills)

        return userinfo, GetResult.Success

    def get_orders(self, jwt_data: JwtData) -> (Orders, GetResult):  # TODO handle admin
        if jwt_data.role == Role.Client:
            orders, result = self.DB_manager.get_client_orders(jwt_data.id)
        else:
            orders, result = self.DB_manager.get_master_orders(jwt_data.id)
        print(f"Account {jwt_data.username} requested orders with status {result}")
        if result == QueryResult.Fail:
            return None, GetResult.Fail
        orders = Orders(orders)
        return orders, GetResult.Success

    def search(self, query: Query):
        pass
