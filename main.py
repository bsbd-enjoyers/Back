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
        return jsonify(SimpleMsg("Bad Json").get_dict()), 400

    resp = jsonify(SimpleResult(False).get_dict())

    token, result = auth.login(auth_class)
    if result == AuthResult.Accept:
        resp = jsonify(SimpleResult(True).get_dict())
        resp.set_cookie("AuthTokenJWT", value=token)

    return resp, 200


@app.route("/check_login", methods=["POST"])
def check_login():
    login_json = request.get_json()

    try:
        check_login_class = CheckLogin(login_json)
    except ValueError as e:
        print(e)
        return jsonify(SimpleMsg("Bad Json").get_dict()), 400

    # print(login_json)
    if auth.check_login_exists(check_login_class):
        return jsonify(SimpleResult(True).get_dict()), 200

    return jsonify(SimpleResult(False).get_dict()), 200


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
            return jsonify(SimpleMsg("Bad Json").get_dict()), 400

        if status != OrderRegister.Registered:
            return jsonify(SimpleMsg(status.value).get_dict()), 400

        update.add_order(order)

        return jsonify(SimpleMsg(status.value).get_dict()), 200

    return "cool", 200  # TODO: do orders first


@app.route("/session", methods=["GET", "POST"])
@web.check_jwt
def session(jwt_data):
    if request.method == "GET":
        return jsonify(provide.get_userinfo(jwt_data).get_dict()), 200

    if request.method == "POST":
        auth.dropsession(jwt_data)
        return "cool", 200  # TODO: then session


@app.route('/register', methods=["POST"])
def register():
    register_json = request.get_json()

    try:
        register_class = RegisterData(register_json)
    except ValueError as e:
        print(e)
        return jsonify(SimpleMsg("Bad Json").get_dict()), 400

    if auth.register(register_class) == RegisterResult.Accept:
        return jsonify(SimpleResult(True).get_dict())

    return jsonify(SimpleResult(False).get_dict())


if __name__ == '__main__':
    app.run("0.0.0.0")
