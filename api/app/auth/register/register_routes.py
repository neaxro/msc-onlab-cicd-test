from flask_restful import Resource, request
from app import api, app
import json

from app.auth.register.register_service import RegisterService
from app.user.user_service import UserService
from app.utils.templater import Templater

class RegisterResource(Resource):
    def __init__(self):
        self.user_service = UserService()
        self.register_service = RegisterService()
        self.templater = Templater()
    
    def post(self):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.register_service.validate_json_format(body)
                
                result = self.user_service.insert_user(body)
                
                return app.response_class(
                    response=self.templater.get_basic_succes_template(
                            status="Registered",
                            data=str(result.inserted_id)
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