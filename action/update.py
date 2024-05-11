from db.db_manager import DataBaseManager, QueryResult
from dto.order import UpdateOrder, Submit, OrderStatus
from enum import Enum
from datetime import datetime
from dto.auth import Role
from dto.simple import DeleteEntity, Entity
from action.auth import Auth, ReturnType


class OperationResult(Enum):
    BadFormat = "Date format is dd.mm.yyyy"
    DateExpired = "Date is expired"
    BadCost = "Something is wrong with the cost"
    EmptyDesc = "Description is empty"
    Registered = "Order registered"
    BadData = "Fields data is bad or has wrong types"
    BadPermissions = "Bad permissions"
    BadOrderStatus = "Order has improper status for this operations"
    Success = "Operation Successful"
    Fail = "Operation Failed"


class Update:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    @staticmethod
    def __check_order_date(order: UpdateOrder):
        try:
            date = datetime.strptime(order.create.deadline, "%d.%m.%Y")
        except ValueError:
            return OperationResult.BadFormat

        if date < datetime.now():
            return OperationResult.DateExpired

        order.create.deadline = date

    @staticmethod
    def __check_cost(order: UpdateOrder):
        if type(order.create.cost) is not int or order.create.cost < 0:
            return OperationResult.BadCost

    @staticmethod
    def __check_empty_desc(order: UpdateOrder):
        if not bool(order.create.desc):
            return OperationResult.EmptyDesc

    @Auth.check_permissions_factory([Role.Client], ReturnType.OneVal)
    def add_order(self, order: UpdateOrder) -> OperationResult:
        status = self.__check_order_date(order)
        status = self.__check_cost(order) if status is None else status
        status = self.__check_empty_desc(order) if status is None else status

        if status is not None:
            return status

        if self.DB_manager.create_order(order)[-1] == QueryResult.Fail:
            return OperationResult.BadData

        return OperationResult.Registered

    @Auth.check_permissions_factory([Role.Client], ReturnType.OneVal)
    def change_client_order_status(self, order: UpdateOrder) -> OperationResult:
        order_status, query_status = self.DB_manager.get_order_status(order)
        if query_status != QueryResult.Success:
            return query_status
        if order_status != OrderStatus.Updated:
            return OperationResult.BadOrderStatus

        if order.submit.submit == Submit.Accept:
            _, result = self.DB_manager.set_client_submit(order)
        else:
            _, result = self.DB_manager.reset_order_created(order)

        if result == QueryResult.Fail:
            return result

        return OperationResult.Success

    def delete_entity(self, entity_info: DeleteEntity) -> OperationResult:
        if entity_info.entity == Entity.Order:
            return self.__delete_order(entity_info)
        else:
            return OperationResult.Fail

    @Auth.check_permissions_factory([Role.Client, Role.Admin], ReturnType.OneVal)
    def __delete_order(self, order: DeleteEntity) -> OperationResult:
        _, query_status = self.DB_manager.delete_order(order)
        if query_status != QueryResult.Success:
            return query_status
        return OperationResult.Success

    @Auth.check_permissions_factory([Role.Master], ReturnType.OneVal)
    def change_master_order_info(self, order: UpdateOrder) -> OperationResult:
        if order.jwt_data.role != Role.Master:
            return OperationResult.BadPermissions

        order_status, query_status = self.DB_manager.get_order_status(order)
        if query_status != QueryResult.Success:
            return query_status
        if order_status != OrderStatus.Created:
            return OperationResult.BadOrderStatus

        _, result = self.DB_manager.set_master_info_order(order)
        if result == QueryResult.Fail:
            return result

        return OperationResult.Success
