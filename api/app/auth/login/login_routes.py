from flask_restful import Resource, request
from app import api, app
import json

from app.auth.login.login_service import LoginService
from app.decorators.token_requires import *
from app.utils.templater import Templater

class LoginResource(Resource):
    def __init__(self):
        self.login_service = LoginService()
        self.templater = Templater()
    
    def post(self):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.login_service.validate_json_format(body)
                
                token = self.login_service.login_user(body)
                                
                return app.response_class(
                    response=self.templater.get_basic_succes_template(
                        status="Logged in",
                        data={ 'token': str(token) }
                    ),
                    status=200,
                    mimetype='application/json'
                )
            
            except Exception as e:
                return app.response_class(
                    response=self.templater.get_basic_error_template(
                        error_message=str(e)
                    ),
                    status=500,
                    mimetype='application/json'
                )
            
            
