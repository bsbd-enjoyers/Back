from db.db_manager import DataBaseManager
from dto.order import Order
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


class Update:
    def __init__(self, dbmanager: DataBaseManager):
        self.DB_manager = dbmanager

    @staticmethod
    def __check_order_date(order: Order):
        try:
            date = datetime.strptime(order.deadline, "%d.%m.%Y")
        except ValueError:
            return OrderRegister.BadFormat

        if date < datetime.now():
            return OrderRegister.DateExpired

        order.deadline = date

    @staticmethod
    def __check_cost(order: Order):
        if type(order.cost) is not int or order.cost < 0:
            return OrderRegister.BadCost

    @staticmethod
    def __check_empty_desc(order: Order):
        if not bool(order.desc):
            return OrderRegister.EmptyDesc

    @staticmethod
    def __check_role(order: Order):
        if not order.jwt_data.role == Role.Client:
            return OrderRegister.BadPermissions

    def add_order(self, order: Order) -> OrderRegister:
        status = self.__check_order_date(order)
        status = self.__check_cost(order) if status is None else status
        status = self.__check_empty_desc(order) if status is None else status
        self.DB_manager.create_order(order)
        if status is None:
            return OrderRegister.Registered
        return status

    def change_order_status(self):
        pass
