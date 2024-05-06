import os
from pymongo import MongoClient
from bson import ObjectId
from app.utils.parsers import *

class RegisterService:
    def __init__(self):
        mongodb_url = os.getenv("MONGODB_CONNECTION_URL")
        db_name = os.getenv("MONGODB_DATABASE_NAME")
        user_collection_name = os.getenv("MONGODB_COLLECTION_USERS")
        
        self.client = MongoClient(mongodb_url)
        self.db = self.client[db_name]
        self.user_collection = self.db[user_collection_name]
        
    def validate_json_format(self, json_data):
        required_fields = ["first_name", "last_name", "username", "email", "password"]

        for field in required_fields:
            if not json_data.get(field):
                raise Exception(f"Field '{field}' is required and cannot be empty.")
