import json

fields_login = [
    "password",
    "username"
]


def validate(json_data, fields):
    for field in fields:
        if not json_data.get(field):
            return False
    return True
