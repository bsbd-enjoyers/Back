from requests import *

check_login_json = {
    "login": "dig"
}
register_json = {
    "login": "dig",
    "password": "pupa",
    "role": "client",
    "fullname": "abobchik",
    "email": "aboba@mail.ru",
    "phone": "88005553535",
}
login_json = {
    "login": "dig",
    "password": "pupa"
}


def print_json(data):
    for key, value in data.items():
        print(f"{key}: {value}")


def register(data):
    print("\nRegister")
    print_json(data)
    s = Session()
    resp = s.post("http://127.0.0.1:5000/register", json=data)
    print("\nResponse")
    print(resp.text)


def check_login(data):
    print("\nCheck_login")
    print_json(data)
    s = Session()
    resp = s.post("http://127.0.0.1:5000/check_login", json=data)
    print("\nResponse")
    print(resp.text)


def login(data):
    print("\nLogin")
    print_json(data)
    s = Session()
    resp = s.post("http://127.0.0.1:5000/login", json=data)
    print("\nResponse")
    print_json(resp.headers)
    print(resp.text)
    resp = s.get("http://127.0.0.1:5000/login")
    print(resp.text)


check_login(check_login_json)
register(register_json)
login(login_json)
