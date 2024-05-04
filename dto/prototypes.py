from flask import jsonify


class DataPrototype:
    def check_empty(self):
        for field, value in self.__dict__.items():
            if value is None:
                raise ValueError(f"Empty Field {field} in DTO {self.__class__}")


class ResponsePrototype:
    def response(self):
        return jsonify(self.__dict__)
