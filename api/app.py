import os
from app import app, api

from app.auth.login.login_routes import LoginResource
from app.auth.register.register_routes import RegisterResource

from app.user.user_routes import UserResource

from app.household.household_routes import HouseholdResource
from app.household.household_detailed_routes import HouseholdDetailedResource
from app.household.invitation.invitation_create_routes import InvitationCreateResource
from app.household.invitation.invitation_accept_routes import InvitationAcceptResource
from app.household.household_user_routes import HouseholdUserResource

from app.household.tasks.task_assign_routes import AssignResource
from app.household.tasks.task_unassign_routes import UnassignResource

from app.household.tasks.task_routes import TaskResource
from app.household.tasks.task_detailed_routes import TaskDetailedResource

from app.household.subtasks.subtask_routes import SubtaskResource

# Auth resources
api.add_resource(LoginResource, '/auth/login')
api.add_resource(RegisterResource, '/auth/register')

# User resources
api.add_resource(UserResource, '/user', '/user/<id>')

# Household resources
api.add_resource(HouseholdResource, '/household', '/household/all', '/household/id/<household_id>')
api.add_resource(HouseholdDetailedResource, '/household', '/household/all/detailed', '/household/id/<household_id>/detailed')
api.add_resource(InvitationCreateResource, '/household/invite/')
api.add_resource(InvitationAcceptResource, '/household/accept-invite/<invitation_token>')
api.add_resource(HouseholdUserResource, '/household', '/household/id/<household_id>/users')

# Task resources
api.add_resource(TaskResource, '/household', '/household/id/<household_id>/tasks', '/household/id/<household_id>/tasks/id/<task_id>')
api.add_resource(TaskDetailedResource, '/household', '/household/id/<household_id>/tasks/all/detailed', '/household/tasks/id/<task_id>/detailed')
api.add_resource(AssignResource, '/tasks/id/<task_id>/assign-to/<user_id>')
api.add_resource(UnassignResource, '/tasks/id/<task_id>/unassign-user')

# Subtask resources
api.add_resource(SubtaskResource, '/subtask/<subtask_id>', '/subtask/add-to/<task_id>', '/subtask/<subtask_id>/remove-from/<task_id>', '/subtask/<subtask_id>/for/<task_id>')

if __name__ == '__main__':
    
    app.run(host="0.0.0.0")
