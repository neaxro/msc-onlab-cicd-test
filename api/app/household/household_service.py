import os, datetime, jwt
from pymongo import MongoClient
from bson import ObjectId
from app.utils.parsers import *
from app.utils.time_management import *
from app.utils.validators import validate_non_empty_array

class HouseholdService:
    def __init__(self):
        mongodb_url = os.getenv("MONGODB_CONNECTION_URL")
        db_name = os.getenv("MONGODB_DATABASE_NAME")
        household_collection_name = os.getenv("MONGODB_COLLECTION_HOUSEHOLDS")
        
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.household_collection = self.db[household_collection_name]
    
    def validate_json_format(self, json_data):
        required_fields = ["_id", "title", "creation_date", "people", "tasks"]

        for field in required_fields:
            if field not in json_data or not json_data[field]:
                raise Exception(f"Field '{field}' is missing or empty in the JSON data.")

        if "people" in json_data:
            validate_non_empty_array(json_data["people"], "people")
        if "tasks" in json_data:
            validate_non_empty_array(json_data["tasks"], "tasks")

    def validate_json_format_modify(self, json_data):
        required_fields = ["title"]

        for field in required_fields:
            if not json_data.get(field):
                raise Exception(f"Field '{field}' is missing in the JSON data.")
    
    def validate_json_format_insert(self, json_data):
        required_fields = ["title"]

        for field in required_fields:
            if not json_data.get(field):
                raise Exception(f"Field '{field}' is missing in the JSON data.")
    
    def get_all(self):
        households = self.household_collection.aggregate([
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'people',
                    'foreignField': '_id',
                    'as': 'people'
                }
            },
            {
                '$project': {
                    "people.password": 0
                }
            }
        ])
        
        return parse_json(households)
    
    def get_all_brief(self):
        pipeline = [
            {
                "$project": {
                    "_id": 1,
                    "title": 1,
                    "no_people": { "$size": "$people" },
                    "no_active_tasks": { "$size": { "$filter": { "input": "$tasks", "as": "task", "cond": { "$eq": ["$$task.done", False] } } } }
                }
            }
        ]
        
        households = self.household_collection.aggregate(pipeline)
        
        return parse_json(households)
    
    def get_by_id(self, household_id):        
        household = self.household_collection.aggregate([
            {
                '$match': {
                    '_id': ObjectId(household_id),
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "people",
                    'foreignField': "_id",
                    'as': "people",
                }
            },
            {
                '$project': {
                    'people.password': 0,
                }
            }
        ])
        
        try:
            return parse_json(household.next())
        except Exception:
            raise Exception(f"Household does not exist with ID: {household_id}")
    
    def insert_household(self, household_data: json, user_token_data):        
        new_household = {
            "title": household_data['title'],
            "creation_date": utcnow(),
            "people": [],
            "tasks": []
        }
        
        result = self.household_collection.insert_one(new_household)

        add_user_result = self.insert_user_to_household(
            household_id=result.inserted_id,
            user_id=user_token_data['id']
        )
        return result
    
    def replace_household(self, id: str, household_data: json):

        household = self.get_by_id(id)
                
        household.pop('_id', None)
        
        household['title'] = household_data['title']
            
        result = self.household_collection.replace_one(
            filter={"_id": ObjectId(id)},
            replacement=dict(household)
        )
        
        return result
    
    def delete_household(self, id: str):
        household = self.get_by_id(id)
        
        result = self.household_collection.delete_one({'_id': ObjectId(id)})
        
        return result
    
    def insert_task_to_household(self, household_id, task):
        result = self.household_collection.update_one(
            filter={
                "_id": ObjectId(household_id)
            },
            update={
                "$push": { "tasks": task }
            }
        )
        
        return result
    
    def get_user_ids_in_household(self, household_id):
        result = self.household_collection.find_one(
            {
                "_id": ObjectId(household_id)
            },
            {
                "people": 1,
                "_id": 0
            }
        ).get('people', [])
        
        return result
    
    def insert_user_to_household(self, household_id, user_id):
        result = self.household_collection.update_one(
            filter={
                "_id": ObjectId(household_id)
            },
            update={
                "$push": { "people": ObjectId(user_id) }
            }
        )
        
        return result

    def get_household_by_id(self, household_id):
        household = self.household_collection.find_one(
            {
                '_id': ObjectId(household_id)
            }
        )
        
        if household is None:
            raise Exception(f"Household does not exist with ID: {household_id}")
        
        return household

    def get_users_from_household(self, household_id):
        
        household = self.get_household_by_id(household_id)
        
        result = self.household_collection.aggregate([
            {
                '$match': {
                '_id': ObjectId(household_id)
                }
            },
            {
                '$project': {
                '_id': 0,
                'people': 1
                }
            },
            {
                '$lookup': {
                    'from': "users",
                    'localField': "people",
                    'foreignField': "_id",
                    'as': "people"
                }
            },
            {
                '$unwind': {
                    'path': '$people',
                }
            },
            {
                '$project': {
                    "_id": "$people._id",
                    "first_name": "$people.first_name",
                    "last_name": "$people.last_name",
                    "username": "$people.username",
                    "email": "$people.email",
                    "profile_picture": "$people.profile_picture",
                }
            }
        ])
        
        return parse_json(result)