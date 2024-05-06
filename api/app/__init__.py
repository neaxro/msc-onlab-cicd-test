from flask import Flask
from flask_restful import Api

app = Flask(__name__)
api = Api(app)

from app.auth.login.login_routes import LoginResource
from app.auth.register.register_routes import RegisterResource
from app.user.user_routes import UserResource
from app.household.household_routes import HouseholdResource
from app.household.tasks.task_routes import TaskResource

# Modification 12