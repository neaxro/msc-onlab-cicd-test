import os, datetime
from pymongo import MongoClient
from bson import ObjectId
from app.utils.parsers import *
from app.utils.time_management import *
from app.utils.validators import validate_non_empty_array
from app.utils.templater import Templater

from app.household.household_service import HouseholdService
from app.household.tasks.task_service import TaskService
from app.user.user_service import UserService

class SubtaskService:
    def __init__(self):
        mongodb_url = os.getenv("MONGODB_CONNECTION_URL")
        db_name = os.getenv("MONGODB_DATABASE_NAME")
        household_collection_name = os.getenv("MONGODB_COLLECTION_HOUSEHOLDS")

        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.household_collection = self.db[household_collection_name]

        self.templater = Templater()
        self.household_service = HouseholdService()
        self.task_service = TaskService()
        self.user_service = UserService()

    def validate_json_format_insert(self, json_data):
        required_fields = ["title", "type"]

        for field in required_fields:
            if field not in json_data or not json_data[field]:
                raise Exception(f"Field '{field}' is missing or empty in the JSON data.")
    
    def validate_json_format_update(self, json_data):
        required_fields = ["title", "done"]

        for field in required_fields:
            if field not in json_data:
                raise Exception(f"Field '{field}' is missing or empty in the JSON data.")

    def get_by_id(self, subtask_id):
        subtask = self.household_collection.aggregate([
            {
                "$unwind": "$tasks"
            },
            {
                "$unwind": "$tasks.subtasks"
            },
            {
                "$match": {
                "tasks.subtasks._id": ObjectId(subtask_id)
                }
            },
            {
                "$replaceRoot": {
                "newRoot": "$tasks.subtasks"
                }
            }
        ])

        try:
            return parse_json(subtask)
        except Exception:
            raise Exception(f"Task does not exist with ID: {subtask_id}")

    def insert_subtask(self, task_id, subtask_data: json):

        # Check if task exists
        task = self.task_service.get_by_id(task_id)

        task_oid = ObjectId(task_id)
        new_subtask = {
            "_id": ObjectId(),
            "title": subtask_data['title'],
            "type": subtask_data['type'],
            "done": "False"
        }

        # Update operation to add the new subtask
        result = self.household_collection.update_one(
            {
                "tasks._id": task_oid
            },
            {
                "$push": {
                    "tasks.$.subtasks": new_subtask
                }
            }
        )

        return result

    def delete_subtask_from_task(self, task_id, subtask_id):
        
        # Check that these exist
        task = self.task_service.get_by_id(task_id)
        subtask = self.get_by_id(subtask_id)

        task_oid = ObjectId(task_id)
        subtask_oid = ObjectId(subtask_id)

        # Update operation to remove the subtask
        result = self.household_collection.update_one(
            {
                "tasks._id": task_oid
            },
            {
                "$pull": {
                    "tasks.$.subtasks": {
                        "_id": subtask_oid
                    }
                }
            }
        )

        return result

    def update_subtask(self, task_id, subtask_id, subtask_data: json):

        # Check that these exist
        task = self.task_service.get_by_id(task_id)
        subtask = self.get_by_id(subtask_id)

        task_oid = ObjectId(task_id)
        subtask_oid = ObjectId(subtask_id)

        subtask_data['_id'] = subtask_oid

        # Update operation to update the subtask
        result = self.household_collection.update_one(
            {
                "tasks._id": task_oid,
                "tasks.subtasks._id": subtask_oid
            },
            {
                "$set": {
                    "tasks.$.subtasks.$[elem]": subtask_data
                }
            },
            array_filters=[
                {
                    "elem._id": subtask_oid
                }
            ]
        )

        return result
