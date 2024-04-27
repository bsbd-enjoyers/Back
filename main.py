from flask import Flask, request, make_response, jsonify
from db.db_manager import DataBaseManager
from action.auth import Auth, AuthResult, RegisterResult, JwtCheckResult
from action.provide import Provide
from dto.auth import *
from dto import SimpleResult
from config import POSTGRESQL_LOGIN, JWT_SECRET
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import JWTManager

app = Flask(__name__)
db_manager = DataBaseManager(POSTGRESQL_LOGIN)
auth = Auth(db_manager)
provide = Provide(db_manager)

app.config["JWT_SECRET_KEY"] = JWT_SECRET
jwt = JWTManager(app)


def get_jwt_token():
    return request.headers.get("Cookie").replace("AuthTokenJWT=", "")


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == "POST":
        login_json = request.get_json()
        try:
            auth_class = AuthData(login_json)
        except ValueError as e:
            print(e)
            return "Bad Json", 400

        resp = jsonify(SimpleResult(False).get_dict())

        token, result = auth.login(auth_class)
        if result == AuthResult.Accept:
            resp = jsonify(SimpleResult(True).get_dict())
            resp.set_cookie("AuthTokenJWT", value=token)

        return resp, 200

    elif request.method == "GET":
        cookies = get_jwt_token()
        print(cookies)

        if cookies is None:
            return "No token", 403

        jwt_data, check_result = auth.check_jwt(cookies)
        print(f"Cookies checked with result {check_result}")

        if check_result == JwtCheckResult.Verified:
            return jsonify(provide.get_userinfo(jwt_data).get_dict()), 200
        else:
            return "Bad token", 403

    return "Bad request", 400


@app.route("/check_login", methods=["POST", "GET"])
def check_login():
    login_json = request.get_json()

    try:
        check_login_class = CheckLogin(login_json)
    except ValueError as e:
        print(e)
        return "Bad Json", 400

    # print(login_json)
    if auth.check_login_exists(check_login_class):
        return jsonify(SimpleResult(True).get_dict()), 200

    return jsonify(SimpleResult(False).get_dict()), 200


@app.route("/search", methods=["POST"])
def search():
    return "cool", 200 # TODO: then then search


@app.route("/orders", methods=["GET", "POST"])
def orders():
    return "cool", 200  # TODO: do orders first


@app.route("/drop_session", methods=["GET"])
def drop_session():
    return "cool", 200 # TODO: then session


@app.route('/register', methods=["POST"])
def register():
    register_json = request.get_json()

    try:
        register_class = RegisterData(register_json)
    except ValueError as e:
        print(e)
        return "Bad Json", 400

    if auth.register(register_class) == RegisterResult.Accept:
        return jsonify(SimpleResult(True).get_dict())

    return jsonify(SimpleResult(False).get_dict())


if __name__ == '__main__':
    app.run("0.0.0.0")
