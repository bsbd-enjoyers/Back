from flask import json


class DataPrototype:
    def check_empty(self):
        for _, value in self.__dict__:
            if value is None:
                raise ValueError(f"Empty Field in DTO {self.__class__}")


class ResponsePrototype:
    def sdf (self):
       pass
