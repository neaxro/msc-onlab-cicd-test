from flask_restful import Resource, request
from app import api, app

from app.household.household_service import HouseholdService
from app.household.invitation.invitation_service import InvitationService
from app.utils.templater import Templater
from app.decorators.token_requires import token_required

class InvitationAcceptResource(Resource):
    def __init__(self):
        self.invitation_service = InvitationService()
        self.templater = Templater()
    
    @token_required
    def post(self, token_data, invitation_token=None):
        try:
            result = self.invitation_service.process_invitation(
                token_data,
                invitation_token
            )
            return app.response_class(
                response=self.templater.get_basic_succes_template(
                    status="Inserted",
                    data=f"Modified {result.modified_count}"
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