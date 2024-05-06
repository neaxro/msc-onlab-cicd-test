import os, datetime
from pymongo import MongoClient
from bson import ObjectId
from app.utils.parsers import *
from app.utils.time_management import *
from app.utils.validators import validate_non_empty_array
from app.utils.templater import Templater

from app.household.household_service import HouseholdService
from app.user.user_service import UserService

class TaskService:
    def __init__(self):
        mongodb_url = os.getenv("MONGODB_CONNECTION_URL")
        db_name = os.getenv("MONGODB_DATABASE_NAME")
        household_collection_name = os.getenv("MONGODB_COLLECTION_HOUSEHOLDS")
        
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.household_collection = self.db[household_collection_name]
        
        self.templater = Templater()
        self.household_service = HouseholdService()
        self.user_service = UserService()
    
    def validate_json_format_insert(self, json_data):
        required_fields = ["title", "description", "due_date"]

        for field in required_fields:
            if field not in json_data or not json_data[field]:
                raise Exception(f"Field '{field}' is missing or empty in the JSON data.")
    
    def validate_json_format_update(self, json_data):
        required_fields = ["creation_date", "description", "done", "due_date", "responsible_id", "subtasks", "title"]

        for field in required_fields:
            if field not in json_data:
                raise Exception(f"Field '{field}' is missing or empty in the JSON data.")

    def insert_task(self, household_id, task_data: json):
                
        for subtask in task_data['subtasks']:
            subtask['_id'] = ObjectId()
            subtask['done'] = False
        
        new_task = {
            "_id": ObjectId(),
            "title": task_data['title'],
            "description": task_data['description'],
            "creation_date": utcnow(),
            "due_date": task_data['due_date'],
            "done": False,
            "responsible_id": ObjectId(task_data['responsible_id']),
            "subtasks": task_data['subtasks']
        }
        
        result = self.household_service.insert_task_to_household(household_id, new_task)
        return result

    def get_by_id(self, task_id):
        task = self.household_collection.aggregate([
            {
                '$match': {
                    "tasks._id": ObjectId(task_id),
                },
            },
            {
                '$unwind': {
                    'path': "$tasks",
                },
            },
            {   "$match": {
                    "tasks._id": ObjectId(task_id)
                }
            },
            {
                '$project': {
                    'creation_date': "$tasks.creation_date",
                    'description': "$tasks.description",
                    'done': "$tasks.done",
                    'due_date': "$tasks.due_date",
                    'responsible_id': "$tasks.responsible_id",
                    'subtasks': "$tasks.subtasks",
                    'title': "$tasks.title",
                    '_id': "$tasks._id",
                },
            },
        ])
        
        try:
            return parse_json(task.next())
        except Exception:
            raise Exception(f"Task does not exist with ID: {task_id}")        

    def get_all(self, houeshold_id):
        tasks = self.household_collection.aggregate([
            {
                '$match': {
                    '_id': ObjectId(houeshold_id),
                },
            },
            {
                '$project': {
                    '_id': 0,
                    'tasks': 1,
                },
            },
            {
                '$unwind': {
                    'path': "$tasks",
                },
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "tasks.responsible_id",
                    'foreignField': "_id",
                    'as': "responsible",
                },
            },
            {
                '$project': {
                    '_id': "$tasks._id",
                    'title': "$tasks.title",
                    'description': "$tasks.description",
                    'creation_date': "$tasks.creation_date",
                    'due_date': "$tasks.due_date",
                    'done': "$tasks.done",
                    'responsible': {
                        '$cond': {
                            'if': { '$eq': [{ '$size': "$responsible" }, 0] },
                            'then': None,
                            'else': { '$arrayElemAt': ["$responsible", 0] }
                        }
                    },
                    'subtasks': "$tasks.subtasks",
                },
            },
            {
                '$project': {
                    'title': 1,
                    'description': 1,
                    'creation_date': 1,
                    'due_date': 1,
                    'done': 1,
                    'responsible': {
                        '$cond': {
                            'if': { '$eq': ["$responsible", None] },
                            'then': None,
                            'else': {
                                '_id': "$responsible._id",
                                'first_name': "$responsible.first_name",
                                'last_name': "$responsible.last_name",
                                'username': "$responsible.username",
                                'email': "$responsible.email",
                                'profile_picture': "$responsible.profile_picture"
                            }
                        }
                    },
                    'subtasks': 1,
                },
            }
        ])

        if tasks is None:
            raise Exception(f"Household does not exist with ID: {houeshold_id}")
        
        return parse_json(tasks)
    
    def get_all_brief(self, household_id):
        houeshold = self.household_service.get_household_by_id(household_id)
        
        tasks = self.household_collection.aggregate([
            {
                '$match': {
                    '_id': ObjectId(household_id),
                },
            },
            {
                '$unwind': "$tasks",
            },
            {
                '$project': {
                    'task_id': "$tasks._id",
                    'done': "$tasks.done",
                    'due_date': "$tasks.due_date",
                    'no_subtasks': { '$size': "$tasks.subtasks" },
                    'responsible_id': "$tasks.responsible_id",
                    'title': "$tasks.title",
                },
            },
        ])
                
        return parse_json(tasks)
    
    def delete_task_from_household(self, household_id, task_id):
        task = self.get_by_id(task_id)
        
        result = self.household_collection.update_one(
            {"_id": ObjectId(household_id)},
            {"$pull": {"tasks": {"_id": ObjectId(task_id)}}}
        )
        
        return result
    
    def assign_user_to_task(self, task_id, user_id):
        task = self.get_by_id(task_id)
        user = self.user_service.get_user_by_id(user_id)
        
        if user is None:
            raise Exception(f"User does not exist with ID: {user_id}")

        result = self.household_collection.update_one(
            {"tasks._id": ObjectId(task_id)},
            {"$set": {"tasks.$.responsible_id": ObjectId(user_id)}}
        )
        
        return result
    
    def unassign_user_to_task(self, task_id):
        task = self.get_by_id(task_id)
        
        result = self.household_collection.update_one(
            {"tasks._id": ObjectId(task_id)},
            {"$set": {"tasks.$.responsible_id": None}}
        )
        
        return result
    
    def update_task(self, household_id, task_id, task_data):
        task = self.get_by_id(task_id)
        
        task_data['_id'] = ObjectId(task_id)
        task_data['responsible_id'] = ObjectId(task_data['responsible_id'])
        
        for subtask in task_data['subtasks']:
            subtask['_id'] = ObjectId(subtask['_id'])
                
        result = self.household_collection.update_one(
            {"_id": ObjectId(household_id), "tasks._id": ObjectId(task_id)},
            {"$set": {"tasks.$": task_data}}
        )
        
        return result
