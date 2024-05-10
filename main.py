from flask import Flask, request
from db.db_manager import DataBaseManager
from action.auth import Auth, AuthResult, RegisterResult, CheckLoginResult
from action.provide import Provide, GetResult
from action.web import Web
from action.update import Update, OrderRegister, UpdateResult
from dto.auth import *
import ssl
from dto.order import UpdateOrder, Action
from dto.simple import *
from config import POSTGRESQL_LOGIN, SSL_KEY, SSL_CERT

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
        query = Query(jwt_data, request.get_json())
    except ValueError as e:
        print(e)
        return SimpleResult(False).response(), 400
    query_result, status = provide.search(query)
    if status != GetResult.Success:
        return SimpleResult(False).response(), 200
    return query_result.response(), 200  # TODO: then then search


@app.route("/orders", methods=["GET", "POST"])
@web.check_jwt
def orders(jwt_data: JwtData):
    if request.method == "POST":
        try:
            order = UpdateOrder(jwt_data, request.get_json())
        except ValueError as e:
            print(e)
            return SimpleMsg("Bad Json").response(), 400

        if order.action == Action.Create:
            status = update.add_order(order)

            if status != OrderRegister.Registered:
                return SimpleResult(False).response(), 400
            print(f"Order registration ended with {status}")
            return SimpleResult(True).response(), 200

        elif order.action == Action.Submit:
            status = update.change_client_order_status(order)
            if status != UpdateResult.Success:
                return SimpleResult(False).response(), 400

            print(f"Order submit ended with {status}")
            return SimpleResult(True).response(), 200

        elif order.action == Action.Update:
            status = update.change_master_order_info(order)
            if status != UpdateResult.Success:
                return SimpleResult(False).response(), 400

            print(f"Order update ended with {status}")
            return SimpleResult(True).response(), 200

        else:
            return SimpleMsg("Bad Request").response(), 400

    if request.method == "GET":
        order_records, result = provide.get_orders(jwt_data)

        if result == GetResult.Fail:
            SimpleMsg("Bad Request").response(), 400

        return order_records.response(), 200

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
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    ssl_context.load_cert_chain(SSL_CERT, SSL_KEY)
    app.run(ssl_context=ssl_context)
