from flask import Flask, request
from db.db_manager import DataBaseManager
from action.auth import Auth, AuthResult, RegisterResult, CheckLoginResult
from action.provide import Provide, GetResult
from action.web import Web
from action.update import Update, OperationResult, OperationResult
from dto.auth import *
import ssl
from dto.order import UpdateOrder, Action, Review
from dto.simple import *
from db.redis_manger import Redis
from config import *

app = Flask(__name__)
db_manager = DataBaseManager(POSTGRESQL_LOGIN_VM, SSH_TUNNEL_POSTGRES)
redis_manager = Redis(REDIS_CONFIG, SSH_TUNNEL_REDIS)
auth = Auth(db_manager, redis_manager)
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
    if type(result) is not CheckLoginResult:
        return SimpleMsg("Bad Json").response(), 400

    return SimpleResult(result.value).response(), 200


@app.route("/search", methods=["POST"])
@web.check_jwt
def search(jwt_data):
    try:
        query = Query(jwt_data, request.get_json())
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400
    query_result, status = provide.search(query)
    print(f"Search ended with result {status}")
    if status != GetResult.Success:
        return SimpleResult(False).response(), 200
    return query_result.response(), 200  # TODO: then then search


@app.route("/manage", methods=["POST"])
@web.check_jwt
def manage(jwt_data):
    try:
        order = ManageEntity(jwt_data, request.get_json())
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400

    status = update.manage_entity(order)
    print(f"Delete ended with result {status}")
    if status != OperationResult.Success:
        return SimpleResult(False).response(), 200

    return SimpleResult(True).response(), 200


@app.route("/info", methods=["POST"])
@web.check_jwt
def get_info(jwt_data):
    try:
        identity = GetIdentity(jwt_data, request.get_json())
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400
    master_info, status = provide.get_master_info(identity)
    if status != GetResult.Success:
        return SimpleResult(False).response(), 400
    return master_info.response(), 200


@app.route("/reviews", methods=["POST"])
@web.check_jwt
def reviews(jwt_data):
    try:
        review = Review(jwt_data, request.get_json())
    except ValueError as e:
        print(e)
        return SimpleMsg("Bad Json").response(), 400
    status = update.add_review(review)
    print(f"Add review ended with status {status}")
    if status != OperationResult.Success:
        return SimpleResult(False).response(), 400
    return SimpleResult(True).response(), 200


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
            print(f"Order registration ended with {status}")
            if status != OperationResult.Registered:
                return SimpleResult(False).response(), 400

            return SimpleResult(True).response(), 200

        elif order.action == Action.Submit:
            status = update.change_client_order_status(order)
            print(f"Order submit ended with {status}")
            if status != OperationResult.Success:
                return SimpleResult(False).response(), 200

            return SimpleResult(True).response(), 200

        elif order.action == Action.Update:
            status = update.change_master_order_info(order)
            print(f"Order update ended with {status}")
            if status != OperationResult.Success:
                return SimpleResult(False).response(), 200

            return SimpleResult(True).response(), 200

        return SimpleMsg("Bad Request").response(), 400

    if request.method == "GET":
        order_records, result = provide.get_orders(jwt_data)

        if result != GetResult.Success:
            return SimpleMsg("Bad Request").response(), 400

        return order_records.response(), 200

    return "cool", 200


@app.route("/session", methods=["GET", "POST"])
@web.check_jwt
def session(jwt_data: JwtData):
    if request.method == "GET":
        if jwt_data.role == Role.Admin:
            return SimpleMsg("admin", "role").response(), 200

        userinfo, result = provide.get_userinfo(jwt_data)
        if result == GetResult.Fail:
            return SimpleMsg("Bad Request").response(), 400

        return userinfo.response(), 200
    if request.method == "POST":
        auth.drop_session(jwt_data)
        return SimpleMsg("Session Dropped").response(), 200

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
