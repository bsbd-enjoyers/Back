from flask import Flask, request, make_response
from db.db_manager import DBmanager
from auth.auth import Auth
from validate.validate import *

app = Flask(__name__)
db_manager = DBmanager()
auth = Auth(db_manager)



@app.route('/login', methods=["POST"])
def hello_world():
    if request.method == "POST":
        try:
            login_json = request.get_json()
        except Exception:
            return 500
        
        if not validate(login_json, fields_login):
            return 400
        
        if auth.login(login_json):
            resp = make_response()
            resp.set_cookie("AuthTokenJWT", value=auth.gen_jwt(login_json["username"]))
        
        return resp, 200
    return 300 