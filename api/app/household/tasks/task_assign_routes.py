from flask_restful import Resource, request
from app import api, app

from app.household.tasks.task_service import TaskService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class AssignResource(Resource):
    def __init__(self):
        self.task_service = TaskService()
        self.templater = Templater()
    
    @token_required
    def patch(self, token_data, task_id, user_id):
        try:
            result = self.task_service.assign_user_to_task(task_id, user_id)
            
            if result.acknowledged:
                return app.response_class(
                    response=self.templater.get_basic_succes_template(
                        status="Assigned",
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