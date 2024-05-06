from flask_restful import Resource, request, reqparse
from app import api, app
import json

from app.user.user_service import UserService
from app.utils.templater import Templater
from app.decorators.token_requires import *

class UserResource(Resource):
    def __init__(self):
        self.user_service = UserService()
        self.templater = Templater()
    
    @token_required
    def get(self, token_data, id=None):
        try:
            if id is not None:
                result = self.user_service.get_user_by_id(id)
                
                return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Success",
                            data=result
                        ),
                        status=200,
                        mimetype='application/json'
                    )
        
            else:
                return app.response_class(
                    response=self.templater.get_basic_error_template(
                            error_message="No id provided."
                        ),
                    status=404,
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
    
    @token_required
    def patch(self, token_data):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.user_service.validate_json_format(body)
                
                result = self.user_service.replace_user(body)
                
                if result.matched_count > 0:
                    return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Updated",
                            data=f"{result.modified_count} modified"
                        ),
                        status=200,
                        mimetype='application/json'
                    )
                
                else:
                    return app.response_class(
                        response=self.templater.get_basic_error_template(
                            error_message="No mach."
                        ),
                        status=404,
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