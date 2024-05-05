from dto.prototypes import DataPrototype, ResponsePrototype
from dto.auth import JwtData, Role
from datetime import datetime
from enum import Enum


class Order(DataPrototype):
    def __init__(self, jwt_data: JwtData, order_json):
        self.jwt_data = jwt_data
        self.desc = order_json.get("desc")
        self.cost = order_json.get("cost")
        self.name = order_json.get("name")
        self.deadline = order_json.get("deadline")
        self.check_empty()


class OrderRecord:
    def __init__(self, record):
        self.order_id = record[0]
        self.deadline = record[1]
        self.cost = record[2]
        self.status = record[3]


class Orders(ResponsePrototype):
    def __init__(self, orders_tuple):
        self.orders = [OrderRecord(order).__dict__ for order in orders_tuple]
