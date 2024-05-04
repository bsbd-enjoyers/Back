from requests import *

check_login_json = {
    "login": "gibuga"
}
register_json = {
    "login": "gibuga",
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
    "login": "gibuga",
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


def register(data, s):
    print("\nRegister")
    print_json(data)
    resp = s.post("http://127.0.0.1:5000/register", json=data)
    print("\nResponse")
    print(resp.text)


def check_login(data, s):
    print("\nCheck_login")
    print_json(data)
    resp = s.post("http://127.0.0.1:5000/check_login", json=data)
    print("\nResponse")
    print(resp.text)


def login(data, s):
    print("\nLogin")
    print_json(data)
    resp = s.post("http://127.0.0.1:5000/login", json=data)
    print("\nResponse")
    print_json(resp.headers)
    print(resp.text)
    resp = s.get("http://127.0.0.1:5000/session")
    print(resp.text)


def add_order(data, s):
    print("\nAdd Order")
    print(data)
    resp = s.post("http://127.0.0.1:5000/orders", json=data)
    print("\n Response")
    print(resp.text)
    pass


s = Session()
#check_login(check_login_json, s)
#register(register_json, s)
login(login_json, s)
add_order(order_json, s)
