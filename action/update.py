from db.db_manager import DataBaseManager, QueryResult
from dto.order import UpdateOrder, Submit, OrderStatus
from enum import Enum
from datetime import datetime
from dto.auth import Role


class OrderRegister(Enum):
    BadFormat = "Date format is dd.mm.yyyy"
    DateExpired = "Date is expired"
    BadCost = "Something is wrong with the cost"
    EmptyDesc = "Description is empty"
    Registered = "Order registered"
    BadPermissions = "Only Client can register orders"
    BadData = "Fields data is bad or has wrong types"


class UpdateResult(Enum):
    Success = 1
    Fail = 0


class Update:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    @staticmethod
    def __check_order_date(order: UpdateOrder):
        try:
            date = datetime.strptime(order.create.deadline, "%d.%m.%Y")
        except ValueError:
            return OrderRegister.BadFormat

        if date < datetime.now():
            return OrderRegister.DateExpired

        order.create.deadline = date

    @staticmethod
    def __check_cost(order: UpdateOrder):
        if type(order.create.cost) is not int or order.create.cost < 0:
            return OrderRegister.BadCost

    @staticmethod
    def __check_empty_desc(order: UpdateOrder):
        if not bool(order.create.desc):
            return OrderRegister.EmptyDesc

    @staticmethod
    def __check_role(order: UpdateOrder) -> OrderRegister:
        if order.jwt_data.role != Role.Client:
            return OrderRegister.BadPermissions

    def add_order(self, order: UpdateOrder) -> OrderRegister:
        status = self.__check_order_date(order)
        status = self.__check_cost(order) if status is None else status
        status = self.__check_empty_desc(order) if status is None else status
        status = self.__check_role(order) if status is None else status

        if status is not None:
            return status

        if self.DB_manager.create_order(order)[-1] == QueryResult.Fail:
            return OrderRegister.BadData

        return OrderRegister.Registered

    def change_client_order_status(self, order: UpdateOrder) -> UpdateResult:
        if order.jwt_data.role != Role.Client:
            return UpdateResult.Fail

        order_status, query_status = self.DB_manager.get_order_status(order)
        if query_status != QueryResult.Success or order_status != OrderStatus.Updated:
            return UpdateResult.Fail

        if order.submit.submit == Submit.Accept:
            _, result = self.DB_manager.set_client_submit(order)
        else:
            _, result = self.DB_manager.reset_order_created(order)

        if result == QueryResult.Fail:
            return UpdateResult.Fail

        return UpdateResult.Success

    def change_master_order_info(self, order: UpdateOrder) -> UpdateResult:
        if order.jwt_data.role != Role.Master:
            return UpdateResult.Fail

        order_status, query_status = self.DB_manager.get_order_status(order)
        if query_status != QueryResult.Success or order_status != OrderStatus.Created:
            return UpdateResult.Fail

        _, result = self.DB_manager.set_master_info_order(order)
        if result == QueryResult.Fail:
            return UpdateResult.Fail

        return UpdateResult.Success
