from flask import Flask, request, make_response
from db.db_manager import DataBaseManager
from auth.auth import Auth
from validate.validate import *
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

        if not validate(login_json, fields_login):
            return 400

        resp = make_response()

        if auth.login(login_json):
            resp.set_cookie("AuthTokenJWT", value=auth.gen_jwt(login_json["username"]))

        return resp, 200
    return 300


@app.route('/register', methods=["POST"])
def register():
    return 200
