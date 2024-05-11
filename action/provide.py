from db.db_manager import DataBaseManager, QueryResult
from dto.auth import JwtData, Role
from dto.user import UserInfo, Users
from dto.simple import Query, Entity
from dto.order import Orders
from action.auth import Auth, ReturnType


class GetResult:
    Fail = "Troubles receiving info"
    Success = "Info received successfully"


class Provide:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    @Auth.check_permissions_factory([Role.Client, Role.Master], ReturnType.TwoVal)
    def get_userinfo(self, jwt_data: JwtData) -> (UserInfo, GetResult):

        if jwt_data.role == Role.Client:
            userinfo, result = self.DB_manager.get_client(jwt_data.username)
        else:
            userinfo, result = self.DB_manager.get_master(jwt_data.username)

        if result == QueryResult.Fail:
            return None, result

        userinfo = UserInfo(userinfo)

        if userinfo.role == "master":
            skills, result = self.DB_manager.get_skills(userinfo.id)
            if result == QueryResult.Fail:
                return None, result
            userinfo.add_skills(skills)

        return userinfo, GetResult.Success

    @Auth.check_permissions_factory([Role.Client, Role.Master], ReturnType.TwoVal)
    def get_orders(self, jwt_data: JwtData) -> (Orders, GetResult):  # TODO handle admin
        if jwt_data.role == Role.Client:
            orders, result = self.DB_manager.get_client_orders(jwt_data.id)
        else:
            orders, result = self.DB_manager.get_master_orders(jwt_data.id)
        print(f"Account {jwt_data.username} requested orders with status {result}")
        if result == QueryResult.Fail:
            return None, result
        orders = Orders(orders)
        return orders, GetResult.Success

    @Auth.check_permissions_factory([Role.Admin, Role.Master], ReturnType.TwoVal)
    def __search_orders(self, query: Query):
        result, status = self.DB_manager.search_order(query.query)
        if status == QueryResult.Fail:
            return None, status
        orders = Orders(result)
        return orders, GetResult.Success

    @Auth.check_permissions_factory([Role.Admin], ReturnType.TwoVal)
    def __search_clients(self, query: Query):
        result, status = self.DB_manager.search_clients(query.query)
        if status == QueryResult.Fail:
            return None, status
        users = Users(result)
        return users, GetResult.Success

    @Auth.check_permissions_factory([Role.Admin], ReturnType.TwoVal)
    def __search_masters(self, query: Query):
        result, status = self.DB_manager.search_masters(query.query)
        if status == QueryResult.Fail:
            return None, status
        users = Users(result)
        return users, GetResult.Success

    def search(self, query: Query) -> (Orders, GetResult):
        if query.entity == Entity.Order:
            return self.__search_orders(query)
        elif query.entity == Entity.Client:
            return self.__search_clients(query)
        else:
            return self.__search_masters(query)
