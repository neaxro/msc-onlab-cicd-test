from flask_restful import Resource, request
from app import api, app

from app.household.tasks.task_service import TaskService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class TaskResource(Resource):
    def __init__(self):
        self.task_service = TaskService()
        self.templater = Templater()
    
    @token_required
    def get(self, token_data, household_id=None):
        try:
            tasks = self.task_service.get_all_brief(household_id)
            
            return app.response_class(
                response=self.templater.get_basic_succes_template(
                    status="Success",
                    data=tasks
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
    def post(self, token_data, household_id=None):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:
                self.task_service.validate_json_format_insert(body)
                
                result = self.task_service.insert_task(household_id, body)
                
                if result.acknowledged:
                    return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Added",
                            data=f"Modified {result.modified_count}"
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
    def delete(self, token_data, household_id, task_id):
        try:
            result = self.task_service.delete_task_from_household(household_id, task_id)
            
            if result.modified_count > 0:
                return app.response_class(
                    response=self.templater.get_basic_succes_template(
                        status="Deleted",
                        data=f"Deleted {result.modified_count}"
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
    def patch(self, token_data, household_id, task_id):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:                
                self.task_service.validate_json_format_update(body)
                
                result = self.task_service.update_task(household_id, task_id, body)
                
                if result.acknowledged:
                    return app.response_class(
                        response=self.templater.get_basic_succes_template(
                            status="Updated",
                            data=f"Updated {result.modified_count}"
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