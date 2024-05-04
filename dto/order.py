from dto.prototypes import DataPrototype
from dto.auth import JwtData, Role
from datetime import datetime
from enum import Enum


class OrderRegister(Enum):
    BadFormat = "Date format is dd.mm.yyyy"
    DateExpired = "Date is expired"
    BadCost = "Something is wrong with the cost"
    EmptyDesc = "Description is empty"
    Registered = "Order registered"
    BadPermissions = "Only Client can register orders"


class Order(DataPrototype):
    def __init__(self, jwt_data: JwtData, order_json):
        self.jwt_data = jwt_data
        self.desc = order_json.get("desc")
        self.cost = order_json.get("cost")
        self.name = order_json.get("name")
        self.deadline = order_json.get("deadline")
        self.check_empty()

    @staticmethod
    def create(jwt_data: JwtData, order_json):
        order = Order(jwt_data, order_json)
        status = order.check_date()
        status = order.check_cost() if status is None else status
        status = order.check_empty_desc() if status is None else status
        if status is None:
            return order, OrderRegister.Registered
        return None, status

    def check_date(self):
        try:
            date = datetime.strptime(self.deadline, "%d.%m.%Y")
        except ValueError:
            return OrderRegister.BadFormat

        if date < datetime.now():
            return OrderRegister.DateExpired

        self.deadline = date

    def check_cost(self):
        if type(self.cost) is not int or self.cost < 0:
            return OrderRegister.BadCost

    def check_empty_desc(self):
        if not bool(self.desc):
            return OrderRegister.EmptyDesc

    def check_role(self):
        if not self.jwt_data.role == Role.Client:
            return OrderRegister.BadPermissions
