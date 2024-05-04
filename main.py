from flask import Flask, request, make_response, jsonify
from db.db_manager import DataBaseManager
from action.auth import Auth, AuthResult, RegisterResult, JwtCheckResult
from action.provide import Provide
from action.web import Web
from action.update import Update
from dto.auth import *
from dto.order import Order, OrderRegister
from dto.simple import SimpleResult, SimpleMsg
from config import POSTGRESQL_LOGIN, JWT_SECRET

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
    if auth.check_login_exists(check_login_class):
        return SimpleResult(True).response(), 200

    return SimpleResult(False).response(), 200


@app.route("/search", methods=["POST"])
@web.check_jwt
def search():
    return "cool", 200  # TODO: then then search


@app.route("/orders", methods=["GET", "POST"])
@web.check_jwt
def orders(jwt_data):
    if request.method == "POST":

        try:
            order, status = Order.create(jwt_data, request.get_json())
        except ValueError as e:
            print(e)
            return SimpleMsg("Bad Json").response(), 400

        if status != OrderRegister.Registered:
            return SimpleMsg(status.value).response(), 400

        update.add_order(order)

        return SimpleMsg(status.value).response(), 200

    return "cool", 200  # TODO: do orders first


@app.route("/session", methods=["GET", "POST"])
@web.check_jwt
def session(jwt_data):
    if request.method == "GET":
        return provide.get_userinfo(jwt_data).response(), 200

    if request.method == "POST":
        auth.drop_session(jwt_data)
        return "cool", 200  # TODO: then session

    return "Bad Request", 400


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
