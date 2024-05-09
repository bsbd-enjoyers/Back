from requests import *
from dataclasses import dataclass

URL = "https://127.0.0.1:5000"

check_login_json = {
    "login": "zippo"
}
register_json = {
    "login": "zippo",
    "password": "pupa",
    "role": "client",
    "fullname": "abobchik",
    "email": "aboba@mail.ru",
    "phone": "88005553535",
    "about_me": "gay",
    "skills": {
        "dota": "5",
        "sex": "0"
    }
}
login_json = {
    "login": "zippo",
    "password": "pupa"
}

order_json = {
    "desc": "ya sosal menya ebali",
    "name": "Searching for podsos",
    "deadline": "12.08.2024",
    "cost": 300
}


def print_json(data):
    for key, value in data.items():
        print(f"{key}: {value}")


def register(data, ses):
    print("\nRegister")
    print_json(data)
    resp = ses.post(f"{URL}/register", json=data, verify=False)
    print("\nResponse")
    print(resp.text)


def check_login(data, ses):
    print("\nCheck_login")
    print_json(data)
    resp = ses.post(f"{URL}/check_login", json=data, verify=False)
    print("\nResponse")
    print(resp.text)


def login(data, ses):
    print("\nLogin")
    print_json(data)
    resp = ses.post(f"{URL}/login", json=data, verify=False)
    print("\nResponse")
    print_json(resp.headers)
    print(resp.text)
    resp = ses.get(f"{URL}/session")
    print(resp.text)


def add_order(data, ses):
    print("\nAdd Order")
    print_json(data)
    resp = ses.post(f"{URL}/orders", json=data, verify=False)
    print("\n Response")
    print(resp.text)
    pass


s = Session()
check_login(check_login_json, s)
#register(register_json, s)
#login(login_json, s)
#add_order(order_json, s)
