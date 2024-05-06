from flask_restful import Resource, request
from app import api, app

from app.household.household_service import HouseholdService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class HouseholdResource(Resource):
    def __init__(self):
        self.household_service = HouseholdService()
        self.templater = Templater()
    
    @token_required
    def get(self, token_data):
        try:
            households = self.household_service.get_all_brief()
            return app.response_class(
                response=self.templater.get_basic_succes_template(
                    status="Done",
                    data=households
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
    
    @token_required
    def post(self, token_data):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.household_service.validate_json_format_insert(body)
                
                result = self.household_service.insert_household(body, token_data)
                
                if result.acknowledged:
                    return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Created",
                            data={'_id': str(result.inserted_id)}
                        ),
                        status=200,
                        mimetype='application/json'
                    )
                
                else:
                    return app.response_class(
                        response=self.templater.get_basic_error_template(
                            error_message="Error occured."
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
    def patch(self, household_id, token_data):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.household_service.validate_json_format_modify(body)
                
                result = self.household_service.replace_household(household_id, body)
                
                if result.matched_count > 0:
                    return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Updated",
                            data=f"Modified {result.modified_count}."
                        ),
                        status=200,
                        mimetype='application/json'
                    )
                
                else:
                    return app.response_class(
                        response=self.templater.get_basic_error_template(
                            error_message="Error occured."
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
    def delete(self, household_id, token_data):
        try:            
            result = self.household_service.delete_household(household_id)
            
            if result.deleted_count > 0:
                return app.response_class(
                    response=self.templater.get_basic_succes_template(
                        status="Deleted",
                        data=f"{str(result.deleted_count)} removed"
                    ),
                    status=200,
                    mimetype='application/json'
                )
            
            else:
                return app.response_class(
                    response=self.templater.get_basic_error_template(
                        error_message="Error occured."
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