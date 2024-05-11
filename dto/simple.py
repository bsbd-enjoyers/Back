from dto.prototypes import ResponsePrototype
from dto.prototypes import DataPrototype
from dto.auth import JwtData
from enum import Enum


class Entity(Enum):
    Master = "master"
    Client = "client"
    Order = "order"


class SimpleResult(ResponsePrototype):
    def __init__(self, result: bool):
        self.result = result


class SimpleMsg(ResponsePrototype):
    def __init__(self, msg):
        self.msg = msg


class DeleteEntity(DataPrototype):
    def __init__(self, jwt_data, data):
        self.jwt_data = jwt_data
        self.entity = Entity(data.get("entity"))
        self.id = data.get("id")
        self.check_empty()


class Query(DataPrototype):
    def __init__(self, jwt_data: JwtData, data):
        self.jwt_data = jwt_data
        self.query = data.get("query")
        self.entity = Entity(data.get("entity"))
        self.check_query()
        self.check_empty()

    def check_query(self):
        if type(self.query) is str and len(self.query) > 2:
            return
        raise ValueError("Query should be str and at least 3 characters long")
