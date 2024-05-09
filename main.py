from flask import Flask, request
from db.db_manager import DataBaseManager
from action.auth import Auth, AuthResult, RegisterResult, CheckLoginResult
from action.provide import Provide, GetResult
from action.web import Web
from action.update import Update, OrderRegister
from dto.auth import *
from dto.order import Order
from dto.simple import SimpleResult, SimpleMsg, Query
from config import POSTGRESQL_LOGIN

app = Flask(__name__)
db_manager = DataBaseManager(POSTGRESQL_LOGIN)
auth = Auth(db_manager)
provide = Provide(db_manager)
web = Web(auth)
update = Update(db_manager)


@app.route('/login', methods=["POST"])
def login():
    login_json = request.get_json()
    try:
        auth_class = AuthData(login_json)
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400

    resp = SimpleResult(False).response()

    token, result = auth.login(auth_class)
    print(f"Login for {auth_class.username} with res {result}")
    if result == AuthResult.Accept:
        resp = SimpleResult(True).response()
        resp.set_cookie("AuthTokenJWT", value=token)

    return resp, 200


@app.route("/check_login", methods=["POST"])
def check_login():
    login_json = request.get_json()

    try:
        check_login_class = CheckLogin(login_json)
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400

    # print(login_json)
    result = auth.check_login_exists(check_login_class)
    if result == CheckLoginResult.error:
        return SimpleMsg("Bad Json").response(), 400

    if result == CheckLoginResult.true:
        return SimpleResult(True).response(), 200

    return SimpleResult(False).response(), 200


@app.route("/search", methods=["POST"])
@web.check_jwt
def search(jwt_data):
    try:
        query = Query(request.get_json())
    except ValueError as e:
        print(e)
        return SimpleMsg("Should query field with 4 characters long query").response(), 400

    return "cool", 200  # TODO: then then search


@app.route("/orders", methods=["GET", "POST"])
@web.check_jwt
def orders(jwt_data: JwtData):
    if request.method == "POST":

        try:
            order = Order(jwt_data, request.get_json())
        except ValueError as e:
            print(e)
            return SimpleMsg("Bad Json").response(), 400

        status = update.add_order(order)

        if status != OrderRegister.Registered:
            return SimpleMsg(status.value).response(), 400

        return SimpleMsg(status.value).response(), 200

    if request.method == "GET":
        order_records, result = provide.get_orders(jwt_data)
        if result == GetResult.Fail:
            SimpleMsg("Bad Request").response(), 400
        return order_records.response()

    return "cool", 200  # TODO: do orders first


@app.route("/session", methods=["GET", "POST"])
@web.check_jwt
def session(jwt_data):
    if request.method == "GET":
        userinfo, result = provide.get_userinfo(jwt_data)
        if result == GetResult.Fail:
            return SimpleMsg("Bad Request").response(), 400

        return userinfo.response(), 200
    if request.method == "POST":
        auth.drop_session(jwt_data)
        return "cool", 200  # TODO: then session

    return SimpleMsg("Bad Request").response(), 400


@app.route('/register', methods=["POST"])
def register():
    register_json = request.get_json()

    try:
        register_class = RegisterData(register_json)
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400

    if auth.register(register_class) == RegisterResult.Accept:
        return SimpleResult(True).response(), 200

    return SimpleResult(False).response(), 200


if __name__ == '__main__':
    app.run("0.0.0.0")
