from action.auth import Auth, JwtCheckResult
from flask import request, jsonify
from dto.simple import SimpleMsg


class Web:
    def __init__(self, auth: Auth):
        self.auth = auth

    @staticmethod
    def __get_jwt_token():
        token = request.headers.get("Cookie")
        if token is None:
            return None
        token = token.replace("AuthTokenJWT=", "")
        #print(token)
        return token

    def check_jwt(self, request_handler):
        def wrapper(*args, **kwargs):
            jwt_token = self.__get_jwt_token()

            if jwt_token is None:
                return SimpleMsg("No token").response(), 403

            jwt_data, check_result = self.auth.check_jwt(jwt_token)
            print(f"Cookies checked with result {check_result}")
            if check_result != JwtCheckResult.Verified:
                return SimpleMsg("Bad Token").response(), 403
            response = request_handler(jwt_data)
            return response

        wrapper.__name__ = request_handler.__name__
        return wrapper
