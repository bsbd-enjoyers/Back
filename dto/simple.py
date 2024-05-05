from dto.prototypes import ResponsePrototype
from dto.prototypes import DataPrototype
from enum import Enum


class SimpleResult(ResponsePrototype):
    def __init__(self, result: bool):
        self.result = result


class SimpleMsg(ResponsePrototype):
    def __init__(self, msg):
        self.msg = msg


class Query(DataPrototype):
    def __init__(self, data):
        self.query = data.get("query")
        self.check_query()
        self.check_empty()

    def check_query(self):
        if type(self.query) is str and len(self.query) > 3:
            raise ValueError("Query should be str and at least 4 characters long")
