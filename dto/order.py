from dto.prototypes import DataPrototype, ResponsePrototype
from dto.auth import JwtData, Role
from datetime import datetime
from enum import Enum


class Action(Enum):
    Submit = "submit"
    Update = "update"
    Create = "create"

    @staticmethod
    def get(value):
        try:
            role = Action(value)
        except ValueError:
            return None
        return role


class Submit(Enum):
    Accept = True
    Decline = False

    @staticmethod
    def get(value):
        try:
            role = Submit(value)
        except ValueError:
            return None
        return role


class OrderStatus(Enum):
    Created = "created"
    Accepted = "accepted"
    Updated = "updated"


class Order(DataPrototype):
    def __init__(self, order_json):
        self.desc = order_json.get("desc")
        self.cost = order_json.get("cost")
        self.name = order_json.get("name")
        self.deadline = order_json.get("deadline")
        self.status = "created"
        self.check_empty()


class ClientOrderSubmit(DataPrototype):
    def __init__(self, data_json):
        self.submit = Submit.get(data_json.get("submit"))
        self.check_empty()


class MasterOrderDesc(DataPrototype):
    def __init__(self, data_json):
        self.product_type = data_json.get("type")
        self.cost = data_json.get("cost")
        self.mater_desc = data_json.get("master_desc")
        self.check_empty()


class UpdateOrder(DataPrototype):
    def __init__(self, jwt_data: JwtData, update_json):
        self.jwt_data = jwt_data
        self.action = Action.get(update_json.get("action"))
        if self.action == Action.Update:
            self.update = MasterOrderDesc(update_json)
            self.order_id = update_json.get("id_order")
        elif self.action == Action.Submit:
            self.submit = ClientOrderSubmit(update_json)
            self.order_id = update_json.get("id_order")
        elif self.action == Action.Create:
            self.create = Order(update_json)
        self.check_empty()


class OrderRecord:
    def __init__(self, record):
        self.order_id = record[0]
        self.deadline = record[1].strftime("%d/%m/%Y")
        self.master_id = record[2]
        self.client_id = record[3]
        self.client_cost = record[4]
        self.master_cost = record[5]
        self.status = record[6]
        self.name = record[7]
        self.type = record[8]
        self.client_desc = record[9]
        self.master_desc = record[10]


class Review(DataPrototype):
    def __init__(self, jwt_data: JwtData, review_data):
        self.jwt_data = jwt_data
        self.comment = review_data.get("comment")
        self.score = review_data.get("score")
        self.order_id = review_data.get("order_id")
        self.check_score()
        self.check_empty()

    def check_score(self):
        if 0 <= self.score <= 5:
            return
        raise ValueError("Score should be 0-5")


class Orders(ResponsePrototype):
    def __init__(self, orders_tuple):
        self.orders = [OrderRecord(order).__dict__ for order in orders_tuple]
