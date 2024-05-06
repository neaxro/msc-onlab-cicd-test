from flask_restful import Resource, request
from app import api, app

from app.household.household_service import HouseholdService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class HouseholdUserResource(Resource):
    def __init__(self):
        self.household_service = HouseholdService()
        self.templater = Templater()
    
    @token_required
    def get(self, token_data, household_id):
        try:
            users = self.household_service.get_users_from_household(household_id)
            return app.response_class(
                response=self.templater.get_basic_succes_template(
                    status="Done",
                    data=users
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