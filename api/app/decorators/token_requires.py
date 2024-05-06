import datetime
from flask import request, jsonify
from flask_restful import Resource
import jwt, json, os
from functools import wraps

from app.utils.templater import Templater
from app import app

# Decorator to check if the request is authorized
def token_required(f):
    """
    Checks if token is provided and it is valid.
    Function must have a \"token_data\" parameter where the token's data will be present.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        templater = Templater()
        token = request.headers.get('Authorization')
        secret_key = os.environ['TOKEN_SECRET_KEY']

        if not token:
            return app.response_class(
                    response=templater.get_basic_error_template(
                        error_message='Token is missing'
                    ),
                    status=500,
                    mimetype='application/json'
                )

        try:
            data = jwt.decode(token.split(' ')[1], secret_key, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return app.response_class(
                    response=templater.get_basic_error_template(
                        error_message='Token has expired'
                    ),
                    status=500,
                    mimetype='application/json'
                )
        except jwt.InvalidTokenError:
            return app.response_class(
                    response=templater.get_basic_error_template(
                        error_message='Invalid token'
                    ),
                    status=500,
                    mimetype='application/json'
                )

        return f(*args, **kwargs, token_data=data)

    return decorated
