from flask import Flask, request, make_response
from db.db_manager import DataBaseManager
from auth.auth import Auth
from dto.auth import *
from dto.response import SimpleResult
from config import POSTGRESQL_LOGIN

app = Flask(__name__)
db_manager = DataBaseManager(POSTGRESQL_LOGIN)
auth = Auth(db_manager)


@app.route('/login', methods=["POST"])
def login():
    if request.method == "POST":

        try:
            login_json = request.get_json()
        except Exception as e:
            print(e)
            return 500

        try:
            auth_class = AuthData(login_json)
        except ValueError as e:
            print(e)
            return 400

        resp = make_response()

        if auth.login(auth_class):
            resp.set_cookie("AuthTokenJWT", value=auth.gen_jwt(auth_class.username))

        return resp, 200
    return 300


@app.route("/check_login", methods=["POST"])
def check_login():
    try:
        login_json = request.get_json()
    except Exception as e:
        print(e)
        return 500

    try:
        check_login_class = CheckLogin(login_json)
    except ValueError as e:
        print(e)
        return 400

    if auth.check_login_exists(check_login_class):
        return SimpleResult(True).make_response()

    return SimpleResult(False).make_response()


@app.route('/register', methods=["POST"])
def register():
    return 200
