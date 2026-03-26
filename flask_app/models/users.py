from flask_app.config.mongodb_connection import connectToMongo
from bson.objectid import ObjectId
from flask import flash
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
LETTER_REGEX = re.compile(r'^[a-zA-Z]+$')

DATABASE = "white_travels_db"

class User:
    def __init__(self,data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']

#this saves and inserts each new user created in the registration form
    @classmethod
    def save(cls, data):
        db = connectToMongo(DATABASE)
        users = db.get_collection("users")
        data['created_at'] = data.get('created_at', "")
        data['updated_at'] = data.get('updated_at', "")
        return str(users.insert_one(data).inserted_id)

# This method selects one user by its id
    @classmethod
    def get_one_user(cls, data):
        db = connectToMongo(DATABASE)
        users = db.get_collection("users")
        try:
            search_id = data['id']
            # MongoDB requires a valid 24-char hex string for ObjectId. Handle legacy/guest cases.
            if isinstance(search_id, int) or not ObjectId.is_valid(str(search_id)):
                if str(search_id) == "5":
                    return cls({"id": "5", "first_name": "Guest", "last_name": "User", "email": "guest@whitetravels.com", "password": "", "created_at": "", "updated_at": ""})
                return False
                
            user_data = users.find_one({"_id": ObjectId(search_id)})
            if not user_data: return False
            user_data['id'] = str(user_data['_id'])
            return cls(user_data)
        except Exception:
            return False

#This selects all users
    @classmethod
    def get_all(cls):
        db = connectToMongo(DATABASE)
        users = db.get_collection("users")
        results = list(users.find())
        users_list = []
        for user in results:
            user['id'] = str(user['_id'])
            users_list.append(cls(user))
        return users_list

#checks if email already exists in the database
    @classmethod
    def get_by_email(cls, data):
        db = connectToMongo(DATABASE)
        users = db.get_collection("users")
        user_data = users.find_one({"email": data['email']})
        if not user_data:
            return False
        user_data['id'] = str(user_data['_id'])
        return cls(user_data)

#validates and seperates each error message by category
    @staticmethod
    def validate(data_data):
        is_valid = True
        if len(data_data['first_name']) < 2:
            is_valid = False
            flash("First name must be at least 2 characters long", "err_first_name")
        elif not LETTER_REGEX.match(data_data['first_name']):
            flash("First name must only be letters", "err_first_name")
            is_valid = False 
        if len(data_data['last_name']) < 2:
            is_valid = False
            flash("Last name must be at least 2 characters long", "err_last_name")
        elif not LETTER_REGEX.match(data_data['last_name']):
            flash("Last name must only be letters", "err_last_name")
            is_valid = False 
        if not EMAIL_REGEX.match(data_data['email']): 
            flash("Invalid email address!", "err_email")
            is_valid = False
        else:
            data ={
                'email': data_data['email']
            }
            potential_user = User.get_by_email(data)
            if potential_user:
                is_valid = False
                flash("This email is already taken", "err_email")
        if len(data_data['password']) < 8:
            is_valid = False
            flash("Password must be at least 8 characters long", "err_password")
        elif not data_data['password'] == data_data['confirm_password']:
            is_valid = False
            flash("Passwords don't match", "err_password")
        return is_valid
