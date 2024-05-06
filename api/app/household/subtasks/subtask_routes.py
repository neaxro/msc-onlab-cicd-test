from flask_restful import Resource, request
from app import api, app

from app.household.subtasks.subtask_service import SubtaskService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class SubtaskResource(Resource):
    def __init__(self):
        self.subtask_service = SubtaskService()
        self.templater = Templater()

    @token_required
    def get(self, token_data, subtask_id=None):
        try:
            subtask = self.subtask_service.get_by_id(subtask_id)

            return app.response_class(
                response=self.templater.get_basic_succes_template(
                    status="Success",
                    data=subtask
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
    def post(self, token_data, task_id=None):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()

            try:
                self.subtask_service.validate_json_format_insert(body)

                result = self.subtask_service.insert_subtask(task_id, body)

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
    def delete(self, token_data, task_id=None, subtask_id=None):
        try:
            result = self.subtask_service.delete_subtask_from_task(task_id, subtask_id)
            
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
    def patch(self, token_data, task_id=None, subtask_id=None):
        request_type = request.headers.get('Content-Type')
        if request_type == 'application/json':
            body = request.get_json()
            
            try:                
                self.subtask_service.validate_json_format_update(body)
                
                result = self.subtask_service.update_subtask(task_id, subtask_id, body)
                
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
